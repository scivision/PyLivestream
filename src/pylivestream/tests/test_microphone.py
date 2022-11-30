"""
timeout= parameter needs to be at least 10 seconds for audio stream to show in FFplay
"""

import sys
from pathlib import Path
import pylivestream as pls
import pytest
import subprocess
import os
import platform
import importlib.resources

sites = ["youtube", "facebook"]

TIMEOUT = 30
CI = os.environ.get("CI", None) in ("true", "True")
WSL = "Microsoft" in platform.uname().release
ini = Path(__file__).parents[1] / "data/pylivestream.json"


@pytest.mark.skipif(sys.version_info < (3, 9), reason="python >= 3.9 required")
def test_microphone_props():

    with importlib.resources.as_file(
        importlib.resources.files("pylivestream.data").joinpath("logo.png")
    ) as logo:
        S = pls.Microphone(ini, websites=sites, image=logo)

        for s in S.streams:
            assert "-re" not in S.streams[s].cmd
            assert S.streams[s].fps is None
            assert S.streams[s].res == [720, 540]

            assert S.streams[s].video_kbps == 800


@pytest.mark.skipif(sys.version_info < (3, 9), reason="python >= 3.9 required")
def test_microphone_image():

    with importlib.resources.as_file(
        importlib.resources.files("pylivestream.data").joinpath("check4k.png")
    ) as img:
        S = pls.Microphone(ini, websites=sites, image=img)

        for s in S.streams:
            assert "-re" not in S.streams[s].cmd
            assert S.streams[s].fps is None
            assert S.streams[s].res == [3840, 2160]

            assert S.streams[s].video_kbps == 4000


@pytest.mark.timeout(TIMEOUT)
@pytest.mark.skipif(CI or WSL, reason="has no audio hardware typically")
def test_stream():
    S = pls.Microphone(ini, websites="localhost", image=None, timeout=10)

    S.golive()


@pytest.mark.skipif(CI or WSL, reason="has no audio hardware typically")
def test_script():
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pylivestream.microphone",
            "localhost",
            str(ini),
            "--yes",
            "--timeout",
            "10",
        ],
        timeout=TIMEOUT,
    )
