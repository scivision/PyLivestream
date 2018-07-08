#!/usr/bin/env python
from pathlib import Path
import PyLivestream as pls
import pytest
import os
import subprocess
from PyLivestream.listener import listener  # noqa: F401

CI = bool(os.environ['CI']) if 'CI' in os.environ else False
rdir = Path(__file__).resolve().parent  # .resolve() is necessary
DEVNULL = subprocess.DEVNULL

sites = ['localhost', 'periscope', 'youtube', 'facebook']
inifn = rdir/'test.ini'


def test_webcam():
    S = pls.Webcam(inifn, sites)
    for s in S.streams:
        assert '-re' not in S.streams[s].cmd
        assert S.streams[s].fps == 30.

        if s == 'periscope':
            assert S.streams[s].video_kbps == 800
        else:
            if int(S.streams[s].res[1]) == 480:
                assert S.streams[s].video_kbps == 500
            elif int(S.streams[s].res[1]) == 720:
                assert S.streams[s].video_kbps == 1800


@pytest.mark.usefixtures("listener")
@pytest.mark.skipif(CI, reason="This is an interactive test")
def test_webcam_stream():
    S = pls.Webcam(inifn, 'localhost-test')
    print('press   q   in terminal to proceed')
    S.golive()


@pytest.mark.usefixtures("listener")
@pytest.mark.skipif(CI, reason="Many CI's don't have webcam hardware")
def test_webcam_script():
    subprocess.check_call(['WebcamLivestream',
                           '-i', str(inifn),
                           'localhost-test', '--yes'],
                          stdout=DEVNULL, timeout=8,
                          cwd=rdir.parent)


if __name__ == '__main__':
    pytest.main()
