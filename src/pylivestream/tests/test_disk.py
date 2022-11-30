import pylivestream as pls


def test_props():
    p = pls.SaveDisk(inifn=None, outfn="")
    assert p.site == "file"
    assert p.video_kbps == 2000
