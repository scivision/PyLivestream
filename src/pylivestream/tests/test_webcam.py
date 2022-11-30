import pylivestream as pls
import pytest

from pathlib import Path
import sys
from pytest import approx
import subprocess
import os
import platform

sites = ["localhost", "youtube", "facebook"]

TIMEOUT = 30
CI = os.environ.get("CI", None) in ("true", "True")
WSL = "Microsoft" in platform.uname().release
ini = Path(__file__).parents[1] / "data/pylivestream.json"


def test_props():
    S = pls.Camera(ini, websites=sites)
    for s in S.streams:
        assert "-re" not in S.streams[s].cmd
        assert S.streams[s].fps == approx(30.0)

        if int(S.streams[s].res[1]) == 480:
            assert S.streams[s].video_kbps == 500
        elif int(S.streams[s].res[1]) == 720:
            assert S.streams[s].video_kbps == 1800


@pytest.mark.timeout(TIMEOUT)
@pytest.mark.skipif(CI or WSL, reason="has no camera typically")
def test_stream():
    S = pls.Camera(ini, websites="localhost", timeout=5)

    S.golive()


@pytest.mark.skipif(CI or WSL, reason="has no camera typically")
def test_script():
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pylivestream.camera",
            "localhost",
            str(ini),
            "--yes",
            "--timeout",
            "5",
        ],
        timeout=TIMEOUT,
    )
