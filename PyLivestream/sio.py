import json
import logging
import subprocess
from pathlib import Path
from typing import Tuple, Union

DEVNULL = subprocess.DEVNULL


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
        raise FileNotFoundError(f'FFmpeg not found at {exe}  {e}.')

    try:
        subprocess.check_call((probeexe, '-h'),
                              stdout=DEVNULL, stderr=DEVNULL)
    except FileNotFoundError as e:
        raise FileNotFoundError(f'FFprobe: {probeexe}  {e}')

    return exe, probeexe


def get_streams(fn: Path, exe: Path) -> Union[None, dict]:
    if not fn:  # audio-only
        return None

    fn = Path(fn).expanduser()

    assert fn.is_file(), f'{fn} is not a file'

    cmd = [str(exe), '-v', 'error', '-print_format', 'json',
           '-show_streams', '-show_format', str(fn)]

    ret = subprocess.check_output(cmd, universal_newlines=True)
# %% decode JSON from FFprobe
    js = json.loads(ret)
    return js['streams']


def get_resolution(fn: Path, exe: Path) -> Union[None, Tuple[int, int]]:
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

    streams = get_streams(fn, exe)
    if streams is None:
        return None

    res = None

    for s in streams:
        if s['codec_type'] != 'video':
            continue
        res = (s['width'], s['height'])

    return res


def get_framerate(fn: Path, exe: Path) -> Union[None, float]:
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

    streams = get_streams(fn, exe)
    if streams is None:
        return None

    fps = None

    for s in streams:
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
