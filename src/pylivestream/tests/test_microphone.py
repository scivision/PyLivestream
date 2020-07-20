"""
timeout= parameter needs to be at least 10 seconds for audio stream to show in FFplay
"""

import pylivestream as pls
import pytest
import subprocess
import os
import platform
import importlib.resources

sites = ["periscope", "youtube", "facebook"]

TIMEOUT = 30
CI = os.environ.get("CI", None) in ("true", "True")
WSL = "Microsoft" in platform.uname().release


def test_microphone_props(periscope_kbps):

    with importlib.resources.path("pylivestream.data", "logo.png") as logo:
        S = pls.Microphone(inifn=None, websites=sites, image=logo, key="abc")

        for s in S.streams:
            assert "-re" not in S.streams[s].cmd
            assert S.streams[s].fps is None
            assert S.streams[s].res == [720, 540]

            if s == "periscope":
                assert S.streams[s].video_kbps == periscope_kbps
            else:
                assert S.streams[s].video_kbps == 800


def test_microphone_image(periscope_kbps):

    with importlib.resources.path("pylivestream.data", "check4k.png") as img:
        S = pls.Microphone(inifn=None, websites=sites, image=img, key="abc")

        for s in S.streams:
            assert "-re" not in S.streams[s].cmd
            assert S.streams[s].fps is None
            assert S.streams[s].res == [3840, 2160]

            if s == "periscope":
                assert S.streams[s].video_kbps == periscope_kbps
            else:
                assert S.streams[s].video_kbps == 4000


@pytest.mark.timeout(TIMEOUT)
@pytest.mark.skipif(CI or WSL, reason="has no audio hardware typically")
def test_stream():
    S = pls.Microphone(inifn=None, websites="localhost", image=None, timeout=10)

    S.golive()


@pytest.mark.skipif(CI or WSL, reason="has no audio hardware typically")
def test_script():
    subprocess.check_call(
        ["MicrophoneLivestream", "localhost", "--yes", "--timeout", "10"], timeout=TIMEOUT
    )
