#!/usr/bin/env python
from pathlib import Path
import pylivestream as pls
import pytest

R = Path(__file__).parent

sites = ['periscope', 'youtube', 'facebook']
inifn = R / 'test.ini'


def test_disk():
    for s in sites:
        p = pls.SaveDisk(inifn, '')
        assert p.site == 'file'
        assert p.video_kbps == 3000


if __name__ == '__main__':
    pytest.main(['-x', __file__])
