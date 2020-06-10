#!/usr/bin/env python
from pathlib import Path
import pylivestream as pls
import pytest
from pytest import approx

R = Path(__file__).parent
VIDFN = R / "bunny.avi"


@pytest.mark.parametrize("fn", ["pylivestream.ini"])
def test_get_ini_file(fn):

    cfg = pls.utils.get_inifile(fn)

    assert isinstance(cfg, str)


@pytest.mark.parametrize("keyin,keyout", [("abc123", "abc123"), (R / "periscope.key", "abcd1234")])
def test_key(keyin, keyout):
    """tests reading of stream key"""
    assert pls.utils.getstreamkey(keyin) == keyout


@pytest.mark.parametrize("key", ["", None], ids=["empty string", "None"])
def test_empty_key(key):
    assert pls.utils.getstreamkey(key) is None


@pytest.mark.parametrize(
    "key,excp", [(R, IsADirectoryError), (R / "nothere.key", FileNotFoundError)]
)
def test_bad_key(key, excp):

    with pytest.raises(excp):
        assert pls.utils.getstreamkey(key) is None


@pytest.mark.parametrize("rex", ("ffmpeg", "ffprobe"))
def test_exe(rex):
    exe = pls.ffmpeg.get_exe(rex)
    assert rex in exe


@pytest.mark.parametrize("inp", (None, ""))
def test_attrs(inp):
    assert pls.utils.get_resolution(inp) is None

    assert pls.utils.get_resolution(VIDFN) == [426, 240]
    assert pls.utils.get_framerate(VIDFN) == approx(24.0)


def test_config_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        pls.Livestream(tmp_path / "nothere.ini", "localhost")


def test_config_default(tmp_path):
    S = pls.Livestream(None, "localhost")
    assert "localhost" in S.site


if __name__ == "__main__":
    pytest.main([__file__])
