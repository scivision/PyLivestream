from __future__ import annotations
import random
from pathlib import Path
import signal
import argparse

from .base import FileIn
from .utils import meta_caption

try:
    from tinytag import TinyTag
except ImportError:
    TinyTag = None


def stream_files(
    ini_file: Path,
    websites: list[str],
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
            playonce(flist, still_image, websites, ini_file, shuffle, usemeta, assume_yes, timeout)
    else:
        playonce(flist, still_image, websites, ini_file, shuffle, usemeta, assume_yes, timeout)


def playonce(
    flist: list[Path],
    image: Path,
    sites: list[str],
    inifn: Path,
    shuffle: bool,
    usemeta: bool,
    yes: bool,
    timeout: float = None,
):

    if shuffle:
        random.shuffle(flist)

    caption: str

    for f in flist:
        if usemeta and TinyTag:
            try:
                caption = meta_caption(TinyTag.get(str(f)))
                print(caption)
            except LookupError:
                caption = None
        else:
            caption = None

        s = FileIn(
            inifn, sites, infn=f, loop=False, image=image, caption=caption, yes=yes, timeout=timeout
        )

        s.golive()


def fileglob(path: Path, glob: str) -> list[Path]:

    path = Path(path).expanduser()

    if not glob:
        glob = "*.avi"

    if path.is_dir():
        flist = sorted(path.glob(glob))
    elif path.is_file():
        flist = [path]
    else:
        raise FileNotFoundError(path)

    return flist


def cli():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    p = argparse.ArgumentParser(description="Livestream a globbed input file list")
    p.add_argument("path", help="path to discover files from")
    p.add_argument(
        "websites",
        help="site to stream, e.g. localhost youtube facebook twitch",
        nargs="+",
    )
    p.add_argument("json", help="JSON file with stream parameters such as key")
    p.add_argument("-glob", help="file glob pattern to stream.")
    p.add_argument("-image", help="static image to display, for audio-only files.")
    p.add_argument("-shuffle", help="shuffle the globbed file list", action="store_true")
    p.add_argument("-loop", help="repeat the globbed file list endlessly", action="store_true")
    p.add_argument("-y", "--yes", help="no confirmation dialog", action="store_true")
    p.add_argument("-nometa", help="do not add metadata caption to video", action="store_false")
    p.add_argument("-t", "--timeout", help="stop streaming after --timeout seconds", type=int)
    P = p.parse_args()

    stream_files(
        ini_file=P.json,
        websites=P.websites,
        assume_yes=P.yes,
        timeout=P.timeout,
        loop=P.loop,
        video_path=P.path,
        glob=P.glob,
        shuffle=P.shuffle,
        still_image=P.image,
        no_meta=P.nometa,
    )


if __name__ == "__main__":
    cli()
