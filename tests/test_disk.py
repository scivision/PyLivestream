#!/usr/bin/env python
from pathlib import Path
import PyLivestream as pls
import pytest
import subprocess

R = Path(__file__).resolve().parent  # .resolve() is necessary
DEVNULL = subprocess.DEVNULL

sites = ['periscope', 'youtube', 'facebook']
inifn = R / 'test.ini'


def test_disk():
    for s in sites:
        p = pls.SaveDisk(inifn, '')
        assert p.site == 'file'
        assert p.video_kbps == 3000


if __name__ == '__main__':
    pytest.main([__file__])
