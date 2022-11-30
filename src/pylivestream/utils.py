from __future__ import annotations
import logging
import contextlib
import subprocess
from pathlib import Path
import sys
import importlib.resources
import shutil

from .ffmpeg import get_meta


def run(cmd: list[str]):
    """
    shell=True for Windows seems necessary to specify devices enclosed by "" quotes
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


def check_device(cmd: list[str]) -> bool:
    try:
        run(cmd)
        ok = True
    except subprocess.CalledProcessError:
        logging.critical(f'device not available, test command failed: \n {" ".join(cmd)}')
        ok = False

    return ok


def check_display(fn: Path = None) -> bool:
    """see if it's possible to display something with a test file"""

    exe = shutil.which("ffplay")

    if not exe:
        raise FileNotFoundError("FFplay not found")

    def _check_disp(fn: Path | contextlib.AbstractContextManager[Path]) -> int:
        cmd = [exe, "-loglevel", "error", "-t", "1.0", "-autoexit", str(fn)]
        return subprocess.run(cmd, timeout=10).returncode

    if fn:
        ret = _check_disp(fn)
    elif sys.version_info >= (3, 9):
        with importlib.resources.as_file(
            importlib.resources.files(f"{__package__}.data").joinpath("logo.png")
        ) as f:
            ret = _check_disp(f)
    else:
        return None

    return ret == 0


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


def get_resolution(fn: Path, exe: str = None) -> list[str]:
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
