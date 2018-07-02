#!/usr/bin/env python
from pathlib import Path
import PyLivestream as pls
import pytest
import os
import subprocess

CI = bool(os.environ['CI']) if 'CI' in os.environ else False
rdir = Path(__file__).resolve().parent  # .resolve() is necessary
DEVNULL = subprocess.DEVNULL

sites = ['periscope', 'youtube', 'facebook']
inifn = rdir/'test.ini'


def test_disk():
    for s in sites:
        p = pls.SaveDisk(inifn, '')
        assert p.site == 'file'
        assert p.video_kbps == 3000


if __name__ == '__main__':
    pytest.main()
