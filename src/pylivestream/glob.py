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
    site: str,
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

        s = FileIn(inifn, site, infn=f, loop=False, image=image, caption=caption, yes=yes)

        s.golive()


def fileglob(path: T.Union[str, Path], glob: str) -> T.List[Path]:

    path = Path(path).expanduser()

    if glob:
        if not path.is_dir():
            raise NotADirectoryError(path)
        flist = list(path.glob(glob))
    else:  # assume single file
        if not path.is_file():
            raise FileNotFoundError(path)
        flist = [path]

    if not flist:
        raise FileNotFoundError(f"did not find files with {path} {glob}")

    return flist
