from pathlib import Path

import pylivestream as pls

ini = Path(__file__).parents[1] / "data/pylivestream.json"


def test_props():
    p = pls.SaveDisk(ini, outfn="")
    assert p.site == "file"
    assert p.video_kbps == 2000
