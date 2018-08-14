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


def test_exe():
    exe, pexe = pls.utils.getexe()
    assert 'ffmpeg' in exe
    assert 'ffprobe' in pexe

    for p in (None, '', 'ffmpeg'):
        exe, pexe = pls.utils.getexe(p)
        assert 'ffmpeg' in exe
        assert 'ffprobe' in pexe


def test_attrs():
    for p in (None, '',):
        assert pls.utils.get_resolution(p) is None

    assert pls.utils.get_resolution(VIDFN) == (426, 240)
    assert pls.utils.get_framerate(VIDFN) == approx(24.0)


if __name__ == '__main__':
    pytest.main(['-x', __file__])
