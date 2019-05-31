import json
import logging
import subprocess
from pathlib import Path
import sys
import shutil
from typing import Tuple, Union, List
import pkg_resources

DEVNULL = subprocess.DEVNULL


def run(cmd: List[str]):
    """
    FIXME: shell=True for Windows seems necessary to specify devices enclosed by "" quotes
    """

    print('\n', ' '.join(cmd), '\n')

    if sys.platform == 'win32':
        subprocess.run(' '.join(cmd), shell=True)
    else:
        subprocess.run(cmd)


"""
This is an error-tolerant way; we haven't found it necessary.
I don't like putting enormous amounts in a PIPE, this can be unstable.
Better to let users know there's a problem.

    ret = subprocess.run(cmd, stderr=subprocess.PIPE, universal_newlines=True)

    if ret.returncode != 0:
        if "Connection reset by peer" in ret.stderr:
            logging.info('input stream (from your computer) ended.')
        else:
            logging.error(ret.stderr)
"""


def check_device(cmd: List[str]) -> bool:
    try:
        run(cmd)
        ok = True
    except subprocess.CalledProcessError:
        logging.critical(f'device not available, test command failed: \n {" ".join(cmd)}')
        ok = False

    return ok


def check_display(fn: Path = None) -> bool:
    """see if it's possible to display something with a test file"""
    if isinstance(fn, Path) and not fn.is_file():
        raise FileNotFoundError(fn)

    if fn is None:
        fn = get_pkgfile('logo.png')

    cmd = ['ffplay', '-v', 'error', '-t', '1.0', '-autoexit', str(fn)]

    ret = subprocess.run(cmd, timeout=10).returncode

    return ret == 0


def get_pkgfile(fn: Union[str, Path]) -> Path:
    fn = Path(fn).expanduser()

    flist: List[Union[str, Path]] = [fn, fn.name]
    for f1 in flist:
        f2 = Path(pkg_resources.resource_filename(__name__, str(f1)))
        if f2.is_file():
            break

        f2 = Path(sys.prefix) / 'share/pylivestream' / f1
        if f2.is_file():
            break

    if not f2.is_file():
        raise FileNotFoundError(fn)

    return f2


def getexe(exein: str = None) -> Tuple[str, str]:
    """checks that host streaming program is installed"""

    if not exein:
        exe = 'ffmpeg'
        probeexe = 'ffprobe'
    else:
        exe = str(Path(exein).expanduser())
        probeexe = str(Path(exein).expanduser().parent / 'ffprobe')
# %% verify
    if not shutil.which(exe):
        print('\n\n *** Must have FFmpeg installed to use PyLivestream.', file=sys.stderr)
        print('https://www.ffmpeg.org/download.html \n\n', file=sys.stderr)
        raise FileNotFoundError(exe)

    if not shutil.which(probeexe):
        print('\n\n *** You must have FFmpeg + FFprobe installed to use PyLivestream.', file=sys.stderr)
        print('https://www.ffmpeg.org/download.html \n\n', file=sys.stderr)
        raise FileNotFoundError(probeexe)

    return exe, probeexe


def get_meta(fn: Path, exein: str = None) -> Union[None, dict]:
    if not fn:  # audio-only
        return None

    fn = Path(fn).expanduser()

    if not fn.is_file():
        raise FileNotFoundError(fn)

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


def get_resolution(fn: Path, exe: str = None) -> List[str]:
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
        res = [s['width'], s['height']]
        break

    return res


def get_framerate(fn: Path, exe: str = None) -> float:
    """
    get framerate of video file
    http://trac.ffmpeg.org/wiki/FFprobeTips#FrameRate

    FFprobe gets framerate from the first video stream in the file it finds.

    Parameters
    ----------
    fn: pathlib.Path
        video filename
    exe: str, optional
        path to ffprobe

    Returns
    -------
    fps: float
        video framerate (frames/second). If not a video file, None is returned.
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
            logging.error(f'FPS not available: {fn}. Is it a video/audio file?')
            fps = None
        break

    return fps


def getstreamkey(keyfn: str) -> str:
    """
    1. read key from ini
    2. if empty, None
    3. if non-empty, see if it's a file to read, or just the key itself.
    """

    if not keyfn:
        return None

    keyp = Path(keyfn).expanduser().resolve(strict=False)
    if keyp.is_file():
        # read only first line in case of trailing blank line
        key = keyp.read_text().split('\n')[0].strip()
    elif keyp.suffix == '.key':
        raise FileNotFoundError(keyp)
    elif keyp.is_dir():
        raise IsADirectoryError(keyp)
    else:
        # assume it's a text key
        key = keyfn

    return key
