"""
importable functions for use from other Python programs

Example:

import pylivestream.api as pls

pls.microphone('localhost')
pls.microphone('twitch')
"""

from __future__ import annotations
from pathlib import Path

from .base import FileIn, Microphone, SaveDisk, Camera
from .glob import stream_files
from .screen import stream_screen

__all__ = [
    "stream_file",
    "stream_files",
    "stream_microphone",
    "stream_camera",
    "stream_screen",
    "capture_screen",
]


def stream_file(
    ini_file: Path,
    websites: str | list[str],
    video_file: Path,
    loop: bool = None,
    assume_yes: bool = False,
    timeout: float = None,
):
    S = FileIn(ini_file, websites, infn=video_file, loop=loop, yes=assume_yes, timeout=timeout)
    sites: list[str] = list(S.streams.keys())
    # %% Go live
    if assume_yes:
        print(f"going live on {sites} with file {video_file}")
    else:
        input(f"Press Enter to go live on {sites} with file {video_file}")
        print("Or Ctrl C to abort.")

    S.golive()


def stream_microphone(
    ini_file: Path,
    websites: list[str],
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


def capture_screen(
    ini_file: Path, *, out_file: Path, assume_yes: bool = False, timeout: float = None
):

    s = SaveDisk(ini_file, out_file, yes=assume_yes, timeout=timeout)
    # %%
    if assume_yes:
        print("saving screen capture to", s.outfn)
    else:
        input(f"Press Enter to screen capture to file {s.outfn}   Or Ctrl C to abort.")

    s.save()


def stream_camera(ini_file: Path, websites: list[str], *, assume_yes: bool, timeout: float):
    S = Camera(ini_file, websites, yes=assume_yes, timeout=timeout)
    sites: list[str] = list(S.streams.keys())
    # %% Go live
    if assume_yes:
        print("going live on", sites)
    else:
        input(f"Press Enter to go live on {sites}.    Or Ctrl C to abort.")

    S.golive()
