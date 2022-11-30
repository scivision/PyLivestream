import pytest
from pytest import approx
from pathlib import Path
import subprocess
import os
import sys
import importlib.resources

import pylivestream as pls

sites = ["youtube", "facebook"]
TIMEOUT = 30
CI = os.environ.get("CI", None) in ("true", "True")
ini = Path(__file__).parents[1] / "data/pylivestream.json"


@pytest.mark.skipif(sys.version_info < (3, 9), reason="python >= 3.9 required")
def test_props():

    with importlib.resources.as_file(
        importlib.resources.files("pylivestream.data").joinpath("bunny.avi")
    ) as fn:
        S = pls.FileIn(ini, websites=sites, infn=fn)
        for s in S.streams:
            assert "-re" in S.streams[s].cmd
            assert S.streams[s].fps == approx(24.0)

            if int(S.streams[s].res[1]) == 480:
                assert S.streams[s].video_kbps == 500
            elif int(S.streams[s].res[1]) == 720:
                assert S.streams[s].video_kbps == 1800


@pytest.mark.skipif(sys.version_info < (3, 9), reason="python >= 3.9 required")
def test_audio():

    with importlib.resources.as_file(
        importlib.resources.files("pylivestream.data").joinpath("logo.png")
    ) as logo, importlib.resources.as_file(
        importlib.resources.files("pylivestream.data").joinpath("orch_short.ogg")
    ) as fn:
        S = pls.FileIn(ini, websites=sites, infn=fn, image=logo)
        for s in S.streams:
            assert "-re" in S.streams[s].cmd
            assert S.streams[s].fps is None

            assert S.streams[s].video_kbps == 400


@pytest.mark.timeout(TIMEOUT)
@pytest.mark.skipif(CI, reason="CI has no audio hardware typically")
@pytest.mark.skipif(sys.version_info < (3, 9), reason="python >= 3.9 required")
def test_simple():
    """stream to localhost"""
    with importlib.resources.as_file(
        importlib.resources.files("pylivestream.data").joinpath("logo.png")
    ) as logo, importlib.resources.as_file(
        importlib.resources.files("pylivestream.data").joinpath("orch_short.ogg")
    ) as fn:
        S = pls.FileIn(ini, websites="localhost", infn=fn, image=logo, yes=True, timeout=5)

        S.golive()


@pytest.mark.skipif(CI, reason="CI has no audio hardware typically")
@pytest.mark.skipif(sys.version_info < (3, 9), reason="python >= 3.9 required")
def test_script():
    with importlib.resources.as_file(
        importlib.resources.files("pylivestream.data").joinpath("bunny.avi")
    ) as fn:
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pylivestream.glob",
                str(fn),
                "localhost",
                str(ini),
                "--yes",
                "--timeout",
                "5",
            ],
            timeout=TIMEOUT,
        )
