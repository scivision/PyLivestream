import logging
import subprocess
from pathlib import Path
import sys
import typing as T
import importlib.resources

from .ffmpeg import get_meta


def run(cmd: T.Sequence[str]):
    """
    FIXME: shell=True for Windows seems necessary to specify devices enclosed by "" quotes
    """

    print("\n", " ".join(cmd), "\n")

    if sys.platform == "win32":
        subprocess.run(" ".join(cmd), shell=True)
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


def check_device(cmd: T.Sequence[str]) -> bool:
    try:
        run(cmd)
        ok = True
    except subprocess.CalledProcessError:
        logging.critical(f'device not available, test command failed: \n {" ".join(cmd)}')
        ok = False

    return ok


def check_display(fn: Path = None) -> bool:
    """see if it's possible to display something with a test file"""

    def _check_disp(fn: Path) -> int:
        cmd = ["ffplay", "-loglevel", "error", "-t", "1.0", "-autoexit", str(fn)]
        return subprocess.run(cmd, timeout=10).returncode

    if fn:
        ret = _check_disp(fn)
    else:
        with importlib.resources.path(f"{__package__}.data", "logo.png") as fn:
            ret = _check_disp(fn)

    return ret == 0


def get_inifile(fn: str) -> str:

    for file in (fn, "~/pylivestream.ini"):
        if not file:
            continue
        inifn = Path(file).expanduser()
        if inifn.is_file():
            return inifn.read_text(errors="ignore")

    return importlib.resources.read_text(__package__, "pylivestream.ini", errors="ignore")


def meta_caption(meta) -> str:
    """makes text from metadata for captioning video"""
    caption = ""

    try:
        caption += meta.title + " - "
    except (TypeError, LookupError, AttributeError):
        pass

    try:
        caption += meta.artist
    except (TypeError, LookupError, AttributeError):
        pass

    return caption


def get_resolution(fn: Path, exe: str = None) -> T.List[str]:
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

    for s in meta["streams"]:
        if s["codec_type"] != "video":
            continue
        res = [s["width"], s["height"]]
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

    for s in meta["streams"]:
        if s["codec_type"] != "video":
            continue
        # https://www.ffmpeg.org/faq.html#toc-AVStream_002er_005fframe_005
        fps = s["avg_frame_rate"]
        fps = list(map(int, fps.split("/")))
        try:
            fps = fps[0] / fps[1]
        except ZeroDivisionError:
            logging.error(f"FPS not available: {fn}. Is it a video/audio file?")
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
        key = keyp.read_text().split("\n")[0].strip()
    elif keyp.suffix == ".key":
        raise FileNotFoundError(keyp)
    elif keyp.is_dir():
        raise IsADirectoryError(keyp)
    else:
        # assume it's a text key
        key = keyfn

    return key
