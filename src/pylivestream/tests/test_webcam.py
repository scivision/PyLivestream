import pylivestream as pls
import pytest
from pytest import approx
import subprocess
import os
import platform

sites = ["localhost", "periscope", "youtube", "facebook"]

TIMEOUT = 30
CI = os.environ.get("CI", None) in ("true", "True")
WSL = "Microsoft" in platform.uname().release


def test_props(periscope_kbps):
    S = pls.Webcam(inifn=None, websites=sites, key="abc")
    for s in S.streams:
        assert "-re" not in S.streams[s].cmd
        assert S.streams[s].fps == approx(30.0)

        if s == "periscope":
            assert S.streams[s].video_kbps == periscope_kbps
        else:
            if int(S.streams[s].res[1]) == 480:
                assert S.streams[s].video_kbps == 500
            elif int(S.streams[s].res[1]) == 720:
                assert S.streams[s].video_kbps == 1800


@pytest.mark.timeout(TIMEOUT)
@pytest.mark.skipif(CI or WSL, reason="has no video hardware typically")
def test_stream():
    S = pls.Webcam(inifn=None, websites="localhost", timeout=5, key="abc")

    S.golive()


@pytest.mark.skipif(CI or WSL, reason="has no vidoe hardware typically")
def test_script():
    subprocess.check_call(
        ["WebcamLivestream", "localhost", "--yes", "--timeout", "5"], timeout=TIMEOUT
    )
