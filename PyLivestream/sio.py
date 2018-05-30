import json
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
    fn = Path(fn).expanduser()

    assert fn.is_file(), f'{fn} is not a file'

    cmd = [str(exe), '-v', 'error', '-print_format', 'json',
           '-show_streams', str(fn)]

    ret = subprocess.check_output(cmd, universal_newlines=True)
# %% decode JSON from FFprobe
    js = json.loads(ret)
    streams = js['streams']
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
    fn = Path(fn).expanduser()

    assert fn.is_file(), f'{fn} is not a file'

    cmd = [str(exe), '-v', 'error', '-print_format', 'json',
           '-show_streams', str(fn)]

    ret = subprocess.check_output(cmd, universal_newlines=True)

# %% decode JSON from FFprobe
    js = json.loads(ret)
    streams = js['streams']
    fps = None

    for s in streams:
        if s['codec_type'] != 'video':
            continue
        # https://www.ffmpeg.org/faq.html#toc-AVStream_002er_005fframe_005
        fps = s['avg_frame_rate']
        fps = list(map(int, fps.split('/')))
        fps = fps[0] / fps[1]

    return fps
