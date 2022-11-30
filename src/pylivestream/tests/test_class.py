import pytest
from pytest import approx
from pathlib import Path
import importlib.resources

import pylivestream as pls


@pytest.mark.parametrize("fn", ["pylivestream.ini"])
def test_get_ini_file(fn):

    cfg = pls.utils.get_inifile(fn)

    assert isinstance(cfg, Path)


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
