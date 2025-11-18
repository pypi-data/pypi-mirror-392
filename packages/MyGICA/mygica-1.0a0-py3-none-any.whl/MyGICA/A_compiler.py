import hashlib
import json
import os
import re
import tomllib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pformat
from typing import Literal, Union

import click
import numpy as np
from PIL import Image
from loguru import logger

from .betterer import subprocess_run
from .structure import parse_config, Range, Text, ProjectConfig
from .time_based_cache_cleaner import TimeBasedCache


@dataclass
class ScriptConfig:
    MyGICA_path: Path
    project: ProjectConfig = None
    output: Path = None
    fontfile: Path = Path("SC-Heavy.otf")
    video_width: int = 1920
    video_height: int = 1080
    cache_dir: Path = Path('cache_dir')
    output_dir: Path = Path('output_dir')
    video_preset: list[str] = field(default_factory=lambda: ['-c:v', 'hevc_nvenc', '-cq', '18', '-pix_fmt', 'p010le'])
    video_preset_cat: list[str] = field(default_factory=lambda: ['-c:v', 'copy', '-c:a', 'copy'])
    video_preset_cat_recode: list[str] = field(default_factory=lambda: ['-c:v', 'hevc_nvenc', '-crf', '18', '-pix_fmt', 'p010le'])

    def __post_init__(self):
        assert self.MyGICA_path.suffixes[-2:] == ['.MyGICA', '.toml'], 'need .MyGICA.toml file'
        assert self.MyGICA_path.exists(), '.MyGICA.toml file should exists'
        assert self.fontfile.exists(), 'font file should exists'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # =============================
        # 解析配置文件，并且生成 ProjectConfig 对象时排除不合法的情况
        # =============================
        with self.MyGICA_path.open('rb') as f:
            self.project = parse_config(tomllib.load(f))

        assert self.project.project_suffix in {'.mp4', '.mkv', '.mov'}, 'output file should be .mp4/.mkv/.mov'
        self.output = self.output_dir / self.MyGICA_path.with_suffix(self.project.project_suffix)
        if hasattr(self, 'video_preset_cat_recode'):
            self.video_preset_cat_recode = ['-r', self.project.fps] + self.video_preset_cat_recode

        assert os.system('ffmpeg -version >nul 2>&1') == 0, 'should install ffmpeg and make sure it is in PATH'
        assert self.project.fps != 23.976, 'fps 23.976 is not supported due to ffmpeg timestamp issues, please use 24000/1001 instead'


# =============================
# 工具函数
# =============================
cache_instance = TimeBasedCache.get_instance()
def subprocess_run_cache(cmd: list[str], files: list[Path], stream_terminal: bool = True):
    """带缓存的 subprocess_run，执行命令后更新文件的时间戳"""
    subprocess_run(cmd, stream_terminal=stream_terminal)
    cache_instance.update(files)


def frame_to_timestamp(frame: int, fps: Union[str, Literal['24000/1001']]) -> str:
    total_seconds = frame_to_time(frame, fps)
    ms = int((total_seconds - int(total_seconds)) * 1000)
    s = int(total_seconds)
    h = s // 3600
    m = (s % 3600) // 60
    s = s % 60
    return f"{h:02}:{m:02}:{s:02}.{ms:03}"


def frame_to_time(frame: int, fps: Union[str, Literal['24000/1001']]) -> float:
    """帧转时间字符串 (HH:MM:SS.mmm)"""
    assert frame >= 0, 'frame should >= 0'
    assert re.compile(r'^[\d/.]+$').match(fps), 'fps should be number or fraction string'
    if '/' in fps:
        num, denom = map(int, fps.split('/'))
        fps = num / denom
    else:
        fps = float(fps)
    total_seconds = frame / fps
    return total_seconds


def escape_toml_string(s: str) -> str:
    """转义字符串用于 drawtext"""
    return s.replace("'", r"\'").replace(":", r"\:")


def is_image(file_path: Path) -> bool:
    """判断文件是否为图片格式"""
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}
    return file_path.suffix.lower() in image_extensions


def build_drawtext_filters(
        texts: list[Text], project: ProjectConfig, fontfile: Path
) -> str:
    """
    构建 ffmpeg drawtext 滤镜字符串，使用指定字体文件，避免 fontconfig 崩溃
    参数:
        texts: 字幕列表，每个元素包含 text, fontsize, fontcolor, y, borderw, bordercolor
        fontfile: 字体文件路径（支持 .ttf, .otf）
        video_width, video_height: 输出分辨率
    返回:
        drawtext 滤镜字符串
    """
    filters: list[str] = []
    for txt in texts:
        # 提取参数，带默认值
        text_str = escape_toml_string(txt.text)
        fontcolor = txt.fontcolor
        fontsize = txt.fontsize
        x = txt.x
        y = txt.y
        borderw = txt.borderw
        bordercolor = txt.bordercolor

        if fontcolor in project.colors:
            fontcolor = project.colors[fontcolor]

        if txt.align == 'center':
            xy = [
                f"x={x}-text_w/2",  # 居中
                f"y={y}-text_h/2",
            ]
        elif txt.align == 'upper left':
            xy = [
                f"x={x}",  # 左上角对齐
                f"y={y}",
            ]

        # 构建 drawtext 参数
        dt_args = \
            [
                f"fontfile={fontfile}",  # 使用指定字体
                f"text='{text_str}'",  # 显示文本
                f"fontcolor={fontcolor}",
                f"fontsize={fontsize}",
            ] + xy + [
                f"borderw={borderw}",
                f"bordercolor={bordercolor}",
            ]
        filters.append(f"drawtext={':'.join(dt_args)}")

    return ",".join(filters)


# =============================
# 缓存剪辑
# =============================
def cache_clip(cmd: list[str], files: list[Path], cache: bool = True, stream_terminal: bool = True) -> Path:
    """使用命令签名缓存剪辑，要求 cmd 最后一个参数为输出文件"""
    # 获取输出文件
    output_file = cmd[-1]
    output_path = Path(output_file)
    if cache:
        # 生成命令签名，保存在文件名中
        cmd_signature = hashlib.md5(' '.join(cmd[:-1]).encode()).hexdigest()
        new_output_path = output_path.with_suffix(f'.{cmd_signature[:6]}{output_path.suffix}')
        for file in files:
            if not file.exists():
                raise FileNotFoundError(f"剪辑时发现文件不存在：{file}")
        # 如果签名文件存在且大小大于0则跳过
        if new_output_path.exists() and new_output_path.stat().st_size > 0:
            logger.info(f"⏭️  使用缓存文件: {new_output_path}")
            return new_output_path

        cmd[-1] = new_output_path.as_posix()  # 更新输出文件名为带签名的文件
    else:
        new_output_path = output_path
    logger.info(f"🎬 执行命令: {' '.join(cmd)}")
    subprocess_run_cache(cmd, files, stream_terminal=stream_terminal)
    logger.info(f"✅ 成功生成: {new_output_path}")
    return new_output_path


# =============================
# 主函数
# =============================
def work(config: ScriptConfig) -> None:
    project = config.project
    logger.info(pformat(project))

    logger.info(f"🎬 开始处理项目: {config.MyGICA_path}")
    segment_files = []

    # =============================
    # 🎬 正常剪辑片段
    # =============================
    for i, rng in enumerate(project.ranges):
        seg_file = config.cache_dir / f"seg_{rng.start}.mp4"
        new_seg_file = work_clips(config, rng, seg_file)
        segment_files.append(new_seg_file)

    # =============================
    # 拼接所有片段
    # =============================
    # no_bgm = config.output.with_stem(config.output.stem + '_no_bgm')
    no_bgm = config.cache_dir / f"no_bgm.mp4"
    no_bgm = cat_video(no_bgm, segment_files, config, config.video_preset_cat)

    # =============================
    # 拼接完成后添加背景音乐 / 在片段中添加背景音乐跳过此处
    # =============================
    output = config.cache_dir / f"output.mp4"
    new_output = add_bgm(Path(project.sources['bgm']), frame_to_time(project.start, project.fps), no_bgm, output)

    # 硬链接到最终输出文件
    config.output.unlink(missing_ok=True)
    os.link(new_output, config.output)

    logger.info(f"\n\n\n🎉🎉🎉 全部处理完成！输出文件: {config.output} 🎉🎉🎉\n\n")

    # 重编码
    if hasattr(config, 'video_preset_cat_recode') and config.video_preset_cat_recode:
        logger.info("♻️ 开始重编码输出文件，增加兼容性，若输出文件已经兼容可无视此步骤")
        output_recode = config.cache_dir / f"output_recode.mp4"
        no_bgm_recode = config.cache_dir / f"no_bgm_recode.mp4"
        new_no_bgm_recode = cat_video(no_bgm_recode, segment_files, config, config.video_preset_cat_recode)
        new_output_recode = add_bgm(Path(project.sources['bgm']), frame_to_time(project.start, project.fps), new_no_bgm_recode, output_recode, stream_terminal=False)
        output = config.output.with_stem(config.output.stem + '_recode')
        # 硬链接到最终输出文件
        output.unlink(missing_ok=True)
        os.link(new_output_recode, output)
        logger.info(f"✅ 重编码完成，输出文件: {output_recode}")


def work_clips(config: ScriptConfig, rng: Range, seg_file: Path) -> Path:
    # 提前生成字幕缓存
    pool = ThreadPoolExecutor()
    futures_text = []
    futures_clip = []
    # 构建字幕滤镜
    texts = rng.texts
    if texts:
        drawtext_filter = build_drawtext_filters(texts, config.project, fontfile=config.fontfile)
        new_seg_file_txt = seg_file.with_stem(seg_file.stem + '_text')
        input_list = new_seg_file_txt.with_suffix('.txt')
        future = pool.submit(get_fade_text, drawtext_filter, input_list, config, rng.end - rng.start)
        futures_text.append(future)
    else:
        drawtext_filter = ""

    segment_files = []
    now_time = rng.start
    for i, clip in enumerate(rng.clips):
        src_path = config.project.sources[clip.source]
        # project_start_time = frame_to_time(now_time, config.project.fps)
        # bgm = config.project.sources['bgm']
        frame_count = clip.end - clip.start  # 精确帧数

        clip_file = seg_file.with_stem(seg_file.stem + f'_{i}') if len(rng.clips) > 1 else seg_file

        af = ['-af', f'volume={clip.volume}dB'] if clip.volume is not None else []
        # af_inline = f'volume={clip.volume}dB' if clip.volume is not None else ''
        # af_in = f'[0:a]{af_inline}[a0_vol];[a0_vol]' if clip.volume is not None else '[0:a]'

        # 判断 source 是否是图片
        if is_image(Path(src_path)):
            # 基础滤镜：缩放和填充
            base_filter = f'scale={config.video_width}:{config.video_height}:force_original_aspect_ratio=decrease,pad={config.video_width}:{config.video_height}:(ow-iw)/2:(oh-ih)/2'

            # 图片 -> 视频：循环 + 精确帧数控制
            cmd = \
                [
                    'ffmpeg', '-y', '-hide_banner',
                    '-f', 'lavfi',  # 使用 lavfi 生成静音
                    '-i', 'anullsrc',
                    '-t', str(frame_to_time(frame_count, config.project.fps)),  # 设置音频时长与视频匹配
                    '-loop', '1',
                    '-i', str(src_path),
                    '-vframes', str(frame_count),  # 精确控制帧数
                    '-r', str(config.project.fps),  # 设置帧率
                    '-vf', base_filter,  # 合并所有滤镜
                    '-pix_fmt', 'yuv420p10le',
                ] + config.video_preset + [str(clip_file)]
            files = [Path(src_path)]
        else:
            # 正常视频处理（保持原来的精确帧数控制）
            start_time = frame_to_timestamp(clip.start, config.project.fps)
            if clip.sound:
                sound_path = config.project.sources[clip.sound]
                # 如果在片段中替换音频
                cmd = [
                    'ffmpeg', '-y', '-hide_banner',
                    '-ss', start_time,
                    '-i', src_path,
                    '-i', sound_path,  # 替换音频
                    '-map', '0:v',
                    '-map', '1:a',
                ]
                files = [Path(src_path), Path(sound_path)]
            else:
                cmd = [
                    'ffmpeg', '-y', '-hide_banner',
                    '-ss', start_time,
                    '-i', src_path,
                ]
                files = [Path(src_path)]
            cmd.extend([
                '-vframes', str(frame_count),  # 使用精确帧数
                '-c:a', 'aac',
                '-b:a', '128k',
                '-ar', '44100',  # 统一采样率
                '-ac', '2',  # 统一声道数
            ])
            cmd.extend(af + config.video_preset + [clip_file.as_posix()])

        logger.info(f"✂️ 剪辑: {clip.source} [{clip.start}:{clip.end}] ({frame_count} 帧) → {clip_file.name}")
        # new_clip_file = cache_clip(cmd, files)
        future = pool.submit(cache_clip, cmd, files)
        futures_clip.append(future)
        # segment_files.append(new_clip_file)
        # assert (res := check_frame(new_clip_file)) == clip.end - clip.start, RuntimeError(f'帧数不匹配, {res} != {clip.end - clip.start}, {new_clip_file.name}')

        now_time += frame_count

    for future in futures_clip:
        segment_files.append(future.result())

    if len(rng.clips) > 1:
        new_seg_file = cat_video(seg_file, segment_files, config, config.video_preset_cat, stream_terminal=False)
        # assert (res := check_frame(seg_file)) == rng.end - rng.start, RuntimeError(f'帧数不匹配, {res} != {rng.end - rng.start}, {seg_file.name}')
    else:
        new_seg_file = segment_files[0]
    # 添加字幕滤镜
    for f in futures_text:
        f.result()
    pool.shutdown()
    if drawtext_filter:
        new_seg_file_txt = seg_file.with_stem(seg_file.stem + '_text')
        input_list = new_seg_file_txt.with_suffix('.txt')
        pattern, text_files = get_fade_text(drawtext_filter, input_list, config, rng.end - rng.start)
        cmd = \
            [
                'ffmpeg', '-y', '-hide_banner',
                '-i', new_seg_file.as_posix(),
                '-framerate', config.project.fps,  # 匹配视频帧率
                '-i', pattern,  # image2 可以，但 concat 不行
                '-filter_complex', "[0:v][1:v]overlay=0:0",
            ] + config.video_preset + [
                new_seg_file_txt.as_posix()
            ]
        files = [new_seg_file, *text_files]
        new_seg_file_txt = cache_clip(cmd, files)
        return new_seg_file_txt

    return new_seg_file


def get_fade_text(drawtext_filter: str, output_list: Path, config: ScriptConfig, length: int) -> tuple[str, list[Path]]:
    """生成淡入淡出字幕的文本文件"""
    transparent_path = config.cache_dir / Path("transparent.png")
    if not transparent_path.exists():
        transparent = np.zeros((config.video_height, config.video_width, 4), dtype=np.uint8)
        Image.fromarray(transparent).save(transparent_path)
    base_text = output_list.with_suffix('.png')
    cmd = [
        "ffmpeg", "-y", "-hide_banner",
        "-i", transparent_path.as_posix(),  # 使用透明背景
        "-vf", drawtext_filter,
        '-frames:v', '1',
        '-update', '1',  # 只输出最后一帧
        base_text
    ]
    files = [transparent_path]
    new_base_text = cache_clip(cmd, files, stream_terminal=False)
    if length <= 20:
        logger.warning(f'字幕持续时间过短，无法应用淡入淡出效果。{length=}')
    file_name = new_base_text.with_stem(new_base_text.stem + '_%04d')
    # 使用缓存
    if Path(file_name.as_posix() % (length - 1)).exists():
        logger.info("⏭️  使用缓存的淡入淡出字幕图片序列")
        return file_name.as_posix(), [Path(file_name.as_posix() % i) for i in range(length)]
    names = get_blur(new_base_text)
    for i in reversed(range(10)):
        Path(file_name.as_posix() % (length - 1 - i)).unlink(missing_ok=True)
        os.link(names[1][i], file_name.as_posix() % (length - 1 - i))
    for i in range(10):
        Path(file_name.as_posix() % i).unlink(missing_ok=True)
        os.link(names[0][i], file_name.as_posix() % i)
    for i in range(10, length - 10):
        Path(file_name.as_posix() % i).unlink(missing_ok=True)
        os.link(new_base_text, file_name.as_posix() % i)
    return file_name.as_posix(), [Path(file_name.as_posix() % i) for i in range(length)]


def get_blur(base_text: Path) -> list[list[Path]]:
    """生成淡入淡出字幕的图片序列"""
    img = Image.open(base_text)
    img_np = np.array(img)

    def rotate(image_np: np.ndarray) -> np.ndarray:
        return image_np[::-1, ::-1, :]

    names = [
        [base_text.with_stem(base_text.stem + f'_{i:02d}') for i in range(10)],
        [base_text.with_stem(base_text.stem + f'-{i:02d}') for i in range(10)],
    ]

    for k in range(2):
        if k == 1: img_np = rotate(img_np)  # noqa: E701
        alpha_channel = img_np[:, :, 3]
        alpha_channel = np.max(alpha_channel, axis=0)
        start = min(np.where(alpha_channel != 0)[0])
        end = max(np.where(alpha_channel != 0)[0])
        step = (end - start) // 10
        for i in range(10):
            mask = np.ones_like(alpha_channel).astype(np.double)
            l = start + i * step
            r = start + (i + 1) * step
            mask[r:] = 0
            mask[l:r] *= 1 - np.arange(step) / step
            new_img_np = img_np.copy().astype(np.double)
            new_img_np[:, :, 3] *= mask[np.newaxis, :]
            if k == 0:
                new_img = Image.fromarray(new_img_np.astype(np.uint8))
            else:
                new_img = Image.fromarray(rotate(new_img_np).astype(np.uint8))
            new_img.save(names[k][i])

    return names


def cat_video(output: Path, segment_files: list[Path], config: ScriptConfig, param: list[str], stream_terminal: bool = True) -> Path:
    """拼接视频"""
    concat_file = config.cache_dir / output.with_suffix('.txt').name
    with concat_file.open('w', encoding='utf-8') as f:
        for seg in segment_files:
            f.write(f"file '{seg.relative_to(config.cache_dir)}'\n")
    new_concat_file = concat_file.with_stem(concat_file.stem + '_' + hashlib.md5(concat_file.read_bytes()).hexdigest()[:6])
    new_concat_file.unlink(missing_ok=True)
    concat_file.rename(new_concat_file)
    logger.info(f"🎥 拼接 {len(segment_files)} 个片段 → {output}")
    cmd = \
        [
            'ffmpeg', '-y', '-hide_banner',
            '-f', 'concat',
            '-i', new_concat_file.as_posix(),
        ] + param + [
            output.as_posix()
        ]
    logger.info(cmd)
    return cache_clip(cmd, segment_files, stream_terminal=stream_terminal)


def add_bgm(bgm: Path, audio_advance_sec: float, input_path: Path, output_path: Path, stream_terminal: bool = True) -> Path:
    """添加背景音乐"""
    logger.info('添加 bgm 并提前', f'{audio_advance_sec=}')

    tmp_output = input_path.parent / output_path.name
    audio_path = tmp_output.with_suffix('.aac')
    cmd = [
        'ffmpeg', '-y', '-hide_banner',
        '-i', input_path.as_posix(),
        '-i', bgm.as_posix(),
        '-filter_complex',
        # 关键修改：对两个音频流都进行aresample和asetpts，确保它们严格同步
        f'[0:a]aresample=async=1:first_pts=0[a0]'  # 处理视频原音频，重置时间戳并异步重采样
        f';[1:a]atrim=start={audio_advance_sec},aresample=async=1[a1]'  # 处理背景音乐
        f';[a0][a1]amix=inputs=2:duration=first:dropout_transition=0[a]'  # 混合
        ,
        '-map', '[a]',
        '-c:a', 'aac',
        '-b:a', '192k',
        audio_path.as_posix(),
    ]
    new_audio_path = cache_clip(cmd, [input_path, bgm], stream_terminal=stream_terminal)

    cmd = \
        [
            'ffmpeg', '-hide_banner',
            '-i', new_audio_path.as_posix(),
            '-af', 'loudnorm=print_format=json',
            '-f', 'null',
            '-'
        ]
    res = subprocess_run(cmd, stream_terminal=False)
    lines: list[str] = [k.strip() for k in res.stderr.splitlines()]
    j = json.loads('\n'.join(lines[lines.index('{'):lines.index('}') + 1]))
    dB = -2 - float(j['input_tp'])  # 目标响度 -2dBTP

    cmd = \
        [
            'ffmpeg', '-y', '-hide_banner',
            '-i', input_path.as_posix(),
            '-i', new_audio_path.as_posix(),
            '-filter_complex',
            f'[1:a]volume={dB}dB[a0]',  # 提升音量
            '-map', '0:v',
            '-map', '[a0]',
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-b:a', '192k',
            tmp_output.as_posix()
        ]
    new_output = cache_clip(cmd, [input_path, new_audio_path], stream_terminal=stream_terminal)
    return new_output


# =============================
# 启动
# =============================
@click.command()
@click.argument('mygica_path', type=click.Path(exists=True, path_type=Path))
@click.option('--font_file', default='SC-Heavy.otf', type=click.Path(path_type=Path), help='字体文件路径', show_default=True)
@click.option('--cache_dir', default='cache_dir', type=click.Path(path_type=Path), help='缓存文件夹路径', show_default=True)
@click.option('--output_dir', default='output_dir', type=click.Path(path_type=Path), help='输出文件夹路径', show_default=True)
def cli(mygica_path: Path, cache_dir: Path, output_dir: Path, font_file: Path) -> None:
    config = ScriptConfig(MyGICA_path=mygica_path, cache_dir=cache_dir, output_dir=output_dir, fontfile=font_file)
    work(config)


if __name__ == '__main__':
    cli()
