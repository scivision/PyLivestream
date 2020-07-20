import pytest

import pylivestream as pls


@pytest.mark.parametrize("site", ["periscope", "youtube", "facebook"])
def test_props(site):
    p = pls.SaveDisk(inifn=None, outfn="")
    assert p.site == "file"
    assert p.video_kbps == 2000
