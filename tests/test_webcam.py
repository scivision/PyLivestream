#!/usr/bin/env python
from pathlib import Path
import pylivestream as pls
import pytest
from pytest import approx
import os
import subprocess
from pylivestream.listener import listener  # noqa: F401

CI = bool(os.environ['CI']) if 'CI' in os.environ else False
R = Path(__file__).parent

sites = ['localhost', 'periscope', 'youtube', 'facebook']
inifn = R / 'test.ini'

S = pls.stream.Stream(inifn, 'localhost-test')
S.osparam()
timelimit = int(S.timelimit[1]) + 3   # allowing 3 seconds leeway


def test_webcam():
    S = pls.Webcam(inifn, sites)
    for s in S.streams:
        assert '-re' not in S.streams[s].cmd
        assert S.streams[s].fps == approx(30.)

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

    S.golive()


@pytest.mark.usefixtures("listener")
@pytest.mark.skipif(CI, reason="Many CI's don't have webcam hardware")
def test_webcam_script():
    subprocess.check_call(['WebcamLivestream',
                           '-i', str(inifn),
                           'localhost-test', '--yes'],
                          timeout=timelimit)


if __name__ == '__main__':
    pytest.main(['-x', __file__])
