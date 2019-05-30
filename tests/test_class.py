#!/usr/bin/env python
from pathlib import Path
import pylivestream as pls
import pytest
from pytest import approx

R = Path(__file__).parent
VIDFN = R / 'bunny.avi'


def test_key():
    """tests reading of stream key"""
    assert pls.utils.getstreamkey('abc123') == 'abc123'
    assert pls.utils.getstreamkey(R / 'periscope.key') == 'abcd1234'
    assert pls.utils.getstreamkey('') is None
    assert pls.utils.getstreamkey(None) is None
    assert pls.utils.getstreamkey(R) is None


@pytest.mark.parametrize('rex', (None, '', 'ffmpeg'))
def test_exe(rex):
    exe, pexe = pls.utils.getexe()
    assert 'ffmpeg' in exe
    assert 'ffprobe' in pexe

    exe, pexe = pls.utils.getexe(rex)
    assert 'ffmpeg' in exe
    assert 'ffprobe' in pexe


@pytest.mark.parametrize('inp', (None, ''))
def test_attrs(inp):
    assert pls.utils.get_resolution(inp) is None

    assert pls.utils.get_resolution(VIDFN) == (426, 240)
    assert pls.utils.get_framerate(VIDFN) == approx(24.0)


def test_config_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        pls.Livestream(tmp_path / 'nothere.ini', 'localhost')


if __name__ == '__main__':
    pytest.main(['-x', __file__])
