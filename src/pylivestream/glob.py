from __future__ import annotations
import random
from pathlib import Path

from .base import FileIn
from .utils import meta_caption

try:
    from tinytag import TinyTag
except ImportError:
    TinyTag = None


def playonce(
    flist: list[Path],
    image: Path,
    sites: list[str],
    inifn: Path,
    shuffle: bool,
    usemeta: bool,
    yes: bool,
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

        s = FileIn(inifn, sites, infn=f, loop=False, image=image, caption=caption, yes=yes)

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
