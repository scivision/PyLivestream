import json
import io
import subprocess
from pathlib import Path
from typing import Tuple

DEVNULL = subprocess.DEVNULL


def getexe(exe:Path=None) -> Tuple[Path,Path]:
    """checks that host streaming program is installed"""

    if not exe:
        exe = 'ffmpeg'
        probeexe = 'ffprobe'
    else:
        probeexe = Path(exe).parent / 'ffprobe'

    exe = Path(exe).expanduser()
    probeexe = Path(probeexe).expanduser()
# %% verify
    try:
        subprocess.check_call((str(exe),'-h'),
                              stdout=DEVNULL, stderr=DEVNULL)
    except FileNotFoundError as e:
        raise FileNotFoundError('FFmpeg not found at {}  {}.'.format(exe,e))

    try:
        subprocess.check_call((str(probeexe),'-h'),
                              stdout=DEVNULL, stderr=DEVNULL)
    except FileNotFoundError as e:
        raise FileNotFoundError('FFprobe not found at {}  {}.'.format(probeexe,e))

    return exe, probeexe


def get_resolution(fn:Path, exe:Path) -> Tuple[int,int]:
    """
    get resolution (widthxheight) of video file
    http://trac.ffmpeg.org/wiki/FFprobeTips#WidthxHeight

    Uses FFprobe to take resolution from the first video stream in the file it finds.

    inputs:
    ------
    fn: Path to the video filename

    outputs:
    -------
    res:  (width,height) in pixels of the video

    if not a video file, None is returned.
    """
    fn = Path(fn).expanduser()

    assert fn.is_file(), '{} is not a file'.format(fn)

    cmd = [str(exe),'-v','error', '-print_format','json',
           '-show_streams', str(fn)]

    ret = subprocess.check_output(cmd, universal_newlines=True)
# %% decode JSON from FFprobe
    js = json.load(io.StringIO(ret))
    streams = js['streams']
    res = None

    for s in streams:
        if s['codec_type'] != 'video':
            continue
        res = (s['width'], s['height'])

    return res


def get_framerate(fn:Path, exe:Path) -> float:
    """
    get framerate of video file
    http://trac.ffmpeg.org/wiki/FFprobeTips#FrameRate

    uses FFprobe to take framerate from the first video stream in the file it finds.

    inputs:
    ------
    fn: Path to the video filename

    outputs:
    -------
    fps: video framerate (frames/second)

    if not a video file, None is returned.
    """
    fn = Path(fn).expanduser()

    assert fn.is_file(), '{} is not a file'.format(fn)

    cmd = [str(exe),'-v','error', '-print_format','json',
       '-show_streams', str(fn)]

    ret = subprocess.check_output(cmd, universal_newlines=True)

# %% decode JSON from FFprobe
    js = json.load(io.StringIO(ret))
    streams = js['streams']
    fps = None

    for s in streams:
        if s['codec_type'] != 'video':
            continue
        fps = s['avg_frame_rate'] # https://www.ffmpeg.org/faq.html#toc-AVStream_002er_005fframe_005frate-is-wrong_002c-it-is-much-larger-than-the-frame-rate_002e
        fps = list(map(int,fps.split('/')))
        fps = fps[0] / fps[1]

    return fps