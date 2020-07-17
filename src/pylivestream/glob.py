import random
from pathlib import Path
import typing as T

from .base import FileIn
from .utils import meta_caption

try:
    from tinytag import TinyTag
except ImportError:
    TinyTag = None


def playonce(
    flist: T.List[Path],
    image: Path,
    sites: T.Sequence[str],
    inifn: Path,
    shuffle: bool,
    usemeta: bool,
    yes: bool,
):

    if shuffle:
        random.shuffle(flist)

    caption: T.Union[str, None]

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


def fileglob(path: Path, glob: str) -> T.List[Path]:

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
