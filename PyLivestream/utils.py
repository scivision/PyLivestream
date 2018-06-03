import json
import logging
import subprocess
from pathlib import Path
import sys
from typing import Tuple, Union, List

DEVNULL = subprocess.DEVNULL


def run(cmd: List[str]):
    print('\n', ' '.join(cmd), '\n')

    subprocess.check_call(cmd)


def getexe(exein: Path=None) -> Tuple[str, str]:
    """checks that host streaming program is installed"""

    if not exein:
        exe = 'ffmpeg'
        probeexe = 'ffprobe'
    else:
        exe = str(Path(exein).expanduser())
        probeexe = str(Path(exein).expanduser().parent / 'ffprobe')
# %% verify
    try:
        subprocess.check_call((exe, '-h'),
                              stdout=DEVNULL, stderr=DEVNULL)
    except FileNotFoundError as e:
        print('\n\n *** You must have FFmpeg installed to use PyLivestream.', file=sys.stderr)
        print('https://www.ffmpeg.org/download.html \n\n', file=sys.stderr)
        raise FileNotFoundError(f'FFmpeg not found at {exe}  {e}.')

    try:
        subprocess.check_call((probeexe, '-h'),
                              stdout=DEVNULL, stderr=DEVNULL)
    except FileNotFoundError as e:
        print('\n\n *** You must have FFmpeg installed to use PyLivestream.', file=sys.stderr)
        print('https://www.ffmpeg.org/download.html \n\n', file=sys.stderr)
        raise FileNotFoundError(f'FFprobe: {probeexe}  {e}')

    return exe, probeexe


def get_meta(fn: Path, exein: Path=None) -> Union[None, dict]:
    if not fn:  # audio-only
        return None

    fn = Path(fn).expanduser()

    if not fn.is_file():
        raise FileNotFoundError(f'{fn} is not a file.')

    exe = getexe()[1] if exein is None else exein

    cmd = [str(exe), '-v', 'error', '-print_format', 'json',
           '-show_streams',
           '-show_format', str(fn)]

    ret = subprocess.check_output(cmd, universal_newlines=True)
# %% decode JSON from FFprobe
    return json.loads(ret)


def meta_caption(meta) -> str:
    """makes text from metadata for captioning video"""
    caption = ''

    try:
        caption += meta.title + ' - '
    except (TypeError, LookupError, AttributeError):
        pass

    try:
        caption += meta.artist
    except (TypeError, LookupError, AttributeError):
        pass

    return caption


def get_resolution(fn: Path, exe: Path=None) -> Union[None, Tuple[int, int]]:
    """
    get resolution (widthxheight) of video file
    http://trac.ffmpeg.org/wiki/FFprobeTips#WidthxHeight

    FFprobe gets resolution from the first video stream in the file it finds.

    inputs:
    ------
    fn: Path to the video filename

    outputs:
    -------
    res:  (width,height) in pixels of the video

    if not a video file, None is returned.
    """

    meta = get_meta(fn, exe)
    if meta is None:
        return None

    res = None

    for s in meta['streams']:
        if s['codec_type'] != 'video':
            continue
        res = (s['width'], s['height'])

    return res


def get_framerate(fn: Path, exe: Path=None) -> Union[None, float]:
    """
    get framerate of video file
    http://trac.ffmpeg.org/wiki/FFprobeTips#FrameRate

    FFprobe gets framerate from the first video stream in the file it finds.

    inputs:
    ------
    fn: Path to the video filename

    outputs:
    -------
    fps: video framerate (frames/second)

    if not a video file, None is returned.
    """

    meta = get_meta(fn, exe)
    if meta is None:
        return None

    fps = None

    for s in meta['streams']:
        if s['codec_type'] != 'video':
            continue
        # https://www.ffmpeg.org/faq.html#toc-AVStream_002er_005fframe_005
        fps = s['avg_frame_rate']
        fps = list(map(int, fps.split('/')))
        try:
            fps = fps[0] / fps[1]
        except ZeroDivisionError:
            logging.error(f'FPS not available:{fn}. Is it a video/audio file?')
            fps = None

    return fps


def getstreamkey(keyfn: str) -> Union[None, str]:
    """
    1. read key from ini
    2. if empty, None
    3. if non-empty, see if it's a file to read, or just the key itself.
    """

    if not keyfn:  # '' or None
        return None

    try:
        keyp: Path = Path(keyfn).expanduser().resolve(strict=True)
        key = keyp.read_text().strip() if keyp.is_file() else None
    except FileNotFoundError:  # not a file, might be the key itself, if not a .key filename
        key = None if keyfn.endswith('.key') else keyfn

    return key
