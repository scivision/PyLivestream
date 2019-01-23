#!/usr/bin/env python
from pathlib import Path
import pylivestream as pls
import pytest

R = Path(__file__).parent

inifn = R / 'test.ini'


@pytest.mark.parametrize('site', ['periscope', 'youtube', 'facebook'])
def test_disk(site):
    p = pls.SaveDisk(inifn, '')
    assert p.site == 'file'
    assert p.video_kbps == 3000


if __name__ == '__main__':
    pytest.main(['-x', __file__])
