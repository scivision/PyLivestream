#!/usr/bin/env python
from pathlib import Path
import pylivestream as pls
import pytest
import subprocess
import os
import platform

R = Path(__file__).parent

sites = ['periscope', 'youtube', 'facebook']
inifn = R.parent / 'stream.ini'

LOGO = R.parent / 'doc' / 'logo.png'
IMG4K = R / 'check4k.png'

TIMEOUT = 30
CI = os.environ.get('CI', None) in ('true', 'True')
WSL = 'Microsoft' in platform.uname().release


def test_props():
    S = pls.Microphone(inifn, sites,
                       image=LOGO)

    for s in S.streams:
        assert '-re' not in S.streams[s].cmd
        assert S.streams[s].fps is None
        assert S.streams[s].res == (720, 540)

        if s == 'periscope':
            assert S.streams[s].video_kbps == 800
        else:
            assert S.streams[s].video_kbps == 800


def test_4Kbg():
    S = pls.Microphone(inifn, sites,
                       image=IMG4K)

    for s in S.streams:
        assert '-re' not in S.streams[s].cmd
        assert S.streams[s].fps is None
        assert S.streams[s].res == (3840, 2160)

        if s == 'periscope':
            assert S.streams[s].video_kbps == 800
        else:
            assert S.streams[s].video_kbps == 4000


@pytest.mark.timeout(TIMEOUT)
@pytest.mark.skipif(CI or WSL, reason='has no audio hardware typically')
def test_stream():
    S = pls.Microphone(inifn, 'localhost', image=LOGO, timeout=5)

    S.golive()


@pytest.mark.skipif(CI or WSL, reason='has no audio hardware typically')
def test_script():
    subprocess.check_call(['MicrophoneLivestream',
                           '-i', str(inifn),
                           'localhost', '--yes', '--timeout', '5'],
                          timeout=TIMEOUT)


if __name__ == '__main__':
    pytest.main(['-x', __file__])
