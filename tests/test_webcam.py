#!/usr/bin/env python
from pathlib import Path
import pylivestream as pls
import pytest
from pytest import approx
import subprocess
import os
import platform

R = Path(__file__).parents[1]

sites = ['localhost', 'periscope', 'youtube', 'facebook']
inifn = R / 'stream.ini'

TIMEOUT = 30
CI = os.environ.get('CI', None) in ('true', 'True')
WSL = 'Microsoft' in platform.uname().release


def test_props():
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


@pytest.mark.timeout(TIMEOUT)
@pytest.mark.skipif(CI or WSL, reason='has no video hardware typically')
def test_stream():
    S = pls.Webcam(inifn, 'localhost', timeout=5)

    S.golive()


@pytest.mark.skipif(CI or WSL, reason='has no vidoe hardware typically')
def test_script():
    subprocess.check_call(['WebcamLivestream',
                           '-i', str(inifn),
                           'localhost', '--yes',
                           '--timeout', '5'],
                          timeout=TIMEOUT)


if __name__ == '__main__':
    pytest.main(['-x', __file__])
