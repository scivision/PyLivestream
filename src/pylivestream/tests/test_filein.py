import pytest
from pytest import approx
import subprocess
import os
import importlib.resources

import pylivestream as pls

sites = ["periscope", "youtube", "facebook"]
TIMEOUT = 30
CI = os.environ.get("CI", None) in ("true", "True")


def test_props(periscope_kbps):

    with importlib.resources.path("pylivestream.data", "bunny.avi") as fn:
        S = pls.FileIn(inifn=None, websites=sites, infn=fn, key="abc")
        for s in S.streams:
            assert "-re" in S.streams[s].cmd
            assert S.streams[s].fps == approx(24.0)

            if s == "periscope":
                assert S.streams[s].video_kbps == periscope_kbps
            else:
                if int(S.streams[s].res[1]) == 480:
                    assert S.streams[s].video_kbps == 500
                elif int(S.streams[s].res[1]) == 720:
                    assert S.streams[s].video_kbps == 1800


def test_audio(periscope_kbps):

    with importlib.resources.path(
        "pylivestream.data", "logo.png"
    ) as logo, importlib.resources.path("pylivestream.data", "orch_short.ogg") as fn:
        S = pls.FileIn(inifn=None, websites=sites, infn=fn, image=logo, key="abc")
        for s in S.streams:
            assert "-re" in S.streams[s].cmd
            assert S.streams[s].fps is None

            if s == "periscope":
                assert S.streams[s].video_kbps == periscope_kbps
            else:
                assert S.streams[s].video_kbps == 400


@pytest.mark.timeout(TIMEOUT)
@pytest.mark.skipif(CI, reason="CI has no audio hardware typically")
def test_simple():
    """stream to localhost"""
    with importlib.resources.path(
        "pylivestream.data", "logo.png"
    ) as logo, importlib.resources.path("pylivestream.data", "orch_short.ogg") as fn:
        S = pls.FileIn(inifn=None, websites="localhost", infn=fn, image=logo, yes=True, timeout=5)

        S.golive()


@pytest.mark.skipif(CI, reason="CI has no audio hardware typically")
def test_script():
    with importlib.resources.path("pylivestream.data", "bunny.avi") as fn:
        subprocess.check_call(
            ["FileGlobLivestream", str(fn), "localhost", "--yes", "--timeout", "5"], timeout=TIMEOUT
        )
