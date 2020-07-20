"""
importable functions for use from other Python programs

Example:

import pylivestream.api as pls

pls.microphone('localhost')
pls.microphone('twitch', key='~/twitch.key')
"""

import typing as T
from pathlib import Path

from .base import FileIn, Microphone, Screenshare, SaveDisk, Webcam
from .glob import fileglob, playonce

__all__ = [
    "stream_file",
    "stream_files",
    "stream_microphone",
    "stream_webcam",
    "stream_screen",
    "capture_screen",
]


def stream_file(
    ini_file: Path,
    websites: T.Sequence[str],
    video_file: Path,
    loop: bool = None,
    assume_yes: bool = False,
    timeout: float = None,
):
    S = FileIn(ini_file, websites, infn=video_file, loop=loop, yes=assume_yes, timeout=timeout)
    sites: T.List[str] = list(S.streams.keys())
    # %% Go live
    if assume_yes:
        print(f"going live on {sites} looping file {video_file}")
    else:
        input(f"Press Enter to go live on {sites}," f"looping file {video_file}")
        print("Or Ctrl C to abort.")

    S.golive()


def stream_files(
    ini_file: Path,
    websites: T.Sequence[str],
    *,
    video_path: Path,
    glob: str = None,
    assume_yes: bool = False,
    loop: bool = None,
    shuffle: bool = None,
    still_image: Path = None,
    no_meta: bool = None,
    timeout: float = None,
):
    # %% file / glob wranging
    flist = fileglob(video_path, glob)

    print("streaming these files. Be sure list is correct! \n")
    print("\n".join(map(str, flist)))
    print()

    if assume_yes:
        print("going live on", websites)
    else:
        input(f"Press Enter to go live on {websites}.    Or Ctrl C to abort.")

    usemeta = no_meta

    if loop:
        while True:
            playonce(flist, still_image, websites, ini_file, shuffle, usemeta, assume_yes)
    else:
        playonce(flist, still_image, websites, ini_file, shuffle, usemeta, assume_yes)


def stream_microphone(
    ini_file: Path,
    websites: T.Sequence[str],
    *,
    still_image: Path = None,
    assume_yes: bool = False,
    timeout: float = None,
):
    """
    livestream audio, with still image background
    """

    s = Microphone(ini_file, websites, image=still_image, yes=assume_yes, timeout=timeout)
    sites = list(s.streams.keys())
    # %% Go live
    if assume_yes:
        print("going live on", sites)
    else:
        input(f"Press Enter to go live on {sites}.    Or Ctrl C to abort.")

    s.golive()


def stream_screen(
    ini_file: Path, websites: T.Sequence[str], *, assume_yes: bool = False, timeout: float = None
):

    S = Screenshare(ini_file, websites, yes=assume_yes, timeout=timeout)
    sites: T.List[str] = list(S.streams.keys())
    # %% Go live
    if assume_yes:
        print("going live on", sites)
    else:
        input(f"Press Enter to go live on {sites}    Or Ctrl C to abort.")

    S.golive()


def capture_screen(
    ini_file: Path, *, out_file: Path, assume_yes: bool = False, timeout: float = None
):

    s = SaveDisk(ini_file, out_file, yes=assume_yes, timeout=timeout)
    # %%
    if assume_yes:
        print("saving screen capture to", s.outfn)
    else:
        input(f"Press Enter to screen capture to file {s.outfn}" "Or Ctrl C to abort.")

    s.save()


def stream_webcam(ini_file: Path, websites: T.Sequence[str], *, assume_yes: bool, timeout: float):
    S = Webcam(ini_file, websites, yes=assume_yes, timeout=timeout)
    sites: T.List[str] = list(S.streams.keys())
    # %% Go live
    if assume_yes:
        print("going live on", sites)
    else:
        input(f"Press Enter to go live on {sites}.    Or Ctrl C to abort.")

    S.golive()
