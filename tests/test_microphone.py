#!/usr/bin/env python
"""
timeout= parameter needs to be at least 10 seconds for audio stream to show in FFplay
"""
from pathlib import Path
import pylivestream as pls
import pytest
import subprocess
import os
import platform

R = Path(__file__).resolve().parent

sites = ['periscope', 'youtube', 'facebook']

LOGO = R.parent / 'doc' / 'logo.png'
IMG4K = R / 'check4k.png'

TIMEOUT = 30
CI = os.environ.get('CI', None) in ('true', 'True')
WSL = 'Microsoft' in platform.uname().release


def test_props(periscope_kbps):
    S = pls.Microphone(inifn=None, websites=sites,
                       image=LOGO, key='abc')

    for s in S.streams:
        assert '-re' not in S.streams[s].cmd
        assert S.streams[s].fps is None
        assert S.streams[s].res == [720, 540]

        if s == 'periscope':
            assert S.streams[s].video_kbps == periscope_kbps
        else:
            assert S.streams[s].video_kbps == 800


def test_4Kbg(periscope_kbps):
    S = pls.Microphone(inifn=None, websites=sites,
                       image=IMG4K, key='abc')

    for s in S.streams:
        assert '-re' not in S.streams[s].cmd
        assert S.streams[s].fps is None
        assert S.streams[s].res == [3840, 2160]

        if s == 'periscope':
            assert S.streams[s].video_kbps == periscope_kbps
        else:
            assert S.streams[s].video_kbps == 4000


@pytest.mark.timeout(TIMEOUT)
@pytest.mark.skipif(CI or WSL, reason='has no audio hardware typically')
def test_stream():
    S = pls.Microphone(inifn=None, websites='localhost', image=None, timeout=10)

    S.golive()


@pytest.mark.skipif(CI or WSL, reason='has no audio hardware typically')
def test_script():
    subprocess.check_call(['MicrophoneLivestream',
                           'localhost', '--yes', '--timeout', '10'],
                          timeout=TIMEOUT, cwd=R.parent)


if __name__ == '__main__':
    pytest.main([__file__])
