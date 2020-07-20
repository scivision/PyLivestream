import pytest
from pytest import approx
import importlib.resources

import pylivestream as pls


@pytest.mark.parametrize("fn", ["pylivestream.ini"])
def test_get_ini_file(fn):

    cfg = pls.utils.get_inifile(fn)

    assert isinstance(cfg, str)


def test_key(tmp_path):
    """ tests reading of stream key: string and file """
    assert pls.utils.getstreamkey("abc123") == "abc123"
    fn = tmp_path / "peri.key"
    fn.write_text("abc432")
    assert pls.utils.getstreamkey(fn) == "abc432"


@pytest.mark.parametrize("key", ["", None], ids=["empty string", "None"])
def test_empty_key(key):
    assert pls.utils.getstreamkey(key) is None


def test_bad_key(tmp_path):

    with pytest.raises(IsADirectoryError):
        assert pls.utils.getstreamkey(tmp_path) is None

    with pytest.raises(FileNotFoundError):
        assert pls.utils.getstreamkey(tmp_path / "notAFile.key") is None


@pytest.mark.parametrize("rex", ("ffmpeg", "ffprobe"))
def test_exe(rex):
    exe = pls.ffmpeg.get_exe(rex)
    assert rex in exe


@pytest.mark.parametrize("inp", (None, ""))
def test_attrs(inp):
    assert pls.utils.get_resolution(inp) is None

    with importlib.resources.path("pylivestream.data", "bunny.avi") as fn:
        assert pls.utils.get_resolution(fn) == [426, 240]
        assert pls.utils.get_framerate(fn) == approx(24.0)


def test_config_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        pls.Livestream(tmp_path / "nothere.ini", "localhost")


def test_config_default(tmp_path):
    S = pls.Livestream(None, "localhost")
    assert "localhost" in S.site
