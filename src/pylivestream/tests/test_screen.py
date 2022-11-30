import pytest
from pytest import approx
import subprocess
import os
import platform
import sys

import pylivestream as pls

sites = ["youtube", "facebook"]

TIMEOUT = 30
CI = os.environ.get("CI", None) in ("true", "True")
WSL = "Microsoft" in platform.uname().release


def test_props():
    S = pls.Screenshare(inifn=None, websites=sites, key="abc")
    for s in S.streams:
        assert "-re" not in S.streams[s].cmd
        assert S.streams[s].fps == approx(30.0)

        assert S.streams[s].video_kbps == 500


@pytest.mark.timeout(TIMEOUT)
@pytest.mark.skipif(CI or WSL, reason="has no GUI")
def test_stream():
    S = pls.Screenshare(inifn=None, websites="localhost", timeout=5, key="abc")

    S.golive()


@pytest.mark.skipif(CI or WSL, reason="no GUI typically")
def test_script():
    subprocess.check_call(
        [sys.executable, "-m", "pylivestream.screen", "localhost", "--yes", "--timeout", "5"],
        timeout=TIMEOUT,
    )
