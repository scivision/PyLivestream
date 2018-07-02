#!/usr/bin/env python
from pathlib import Path
import PyLivestream as pls
import pytest
import os
import subprocess
import math
from PyLivestream.listener import listener  # noqa: F401

CI = bool(os.environ['CI']) if 'CI' in os.environ else False
rdir = Path(__file__).resolve().parent  # .resolve() is necessary
DEVNULL = subprocess.DEVNULL

sites = ['periscope', 'youtube', 'facebook']
inifn = rdir/'test.ini'


def test_screenshare():
    S = pls.Screenshare(inifn, sites)
    for s in S.streams:
        assert '-re' not in S.streams[s].cmd
        assert math.isclose(S.streams[s].fps, 30.)

        if s == 'periscope':
            assert S.streams[s].video_kbps == 800
        else:
            assert S.streams[s].video_kbps == 1800


@pytest.mark.skipif(CI, reason="Many CI's don't have video hardware")
def test_screenshare_stream():
    S = pls.Screenshare(inifn, 'localhost')
    print('press   q   in terminal to proceed')
    S.golive()


@pytest.mark.usefixtures("listener")
@pytest.mark.skipif(CI, reason="Many CI's don't have audio hardware")
def test_webcam_script():
    subprocess.check_call(['ScreenshareLivestream',
                           '-i', str(inifn),
                           'localhost-test', '--yes'],
                          stdout=DEVNULL, timeout=8,
                          cwd=rdir.parent)


if __name__ == '__main__':
    pytest.main()
