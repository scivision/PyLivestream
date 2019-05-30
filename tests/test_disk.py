#!/usr/bin/env python
import pylivestream as pls
import pytest


@pytest.mark.parametrize('site', ['periscope', 'youtube', 'facebook'])
def test_props(site):
    p = pls.SaveDisk(inifn=None, outfn='')
    assert p.site == 'file'
    assert p.video_kbps == 2000


if __name__ == '__main__':
    pytest.main(['-x', __file__])
