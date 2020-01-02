#!/usr/bin/env python
import sys
from pathlib import Path
import pylivestream as pls
import pytest
from pytest import approx
import subprocess
import os

R = Path(__file__).resolve().parent

sites = ['periscope', 'youtube', 'facebook']

VIDFN = R / 'bunny.avi'
LOGO = R.parent / 'doc' / 'logo.png'
TIMEOUT = 30

CI = os.environ.get('CI', None) in ('true', 'True')


def test_props(periscope_kbps):
    S = pls.FileIn(inifn=None, websites=sites, infn=VIDFN, key='abc')
    for s in S.streams:
        assert '-re' in S.streams[s].cmd
        assert S.streams[s].fps == approx(24.)

        if s == 'periscope':
            assert S.streams[s].video_kbps == periscope_kbps
        else:
            if int(S.streams[s].res[1]) == 480:
                assert S.streams[s].video_kbps == 500
            elif int(S.streams[s].res[1]) == 720:
                assert S.streams[s].video_kbps == 1800


def test_audio(periscope_kbps):
    flist = list(R.glob('*.ogg'))

    S = pls.FileIn(inifn=None, websites=sites, infn=flist[0], image=LOGO, key='abc')
    for s in S.streams:
        assert '-re' in S.streams[s].cmd
        assert S.streams[s].fps is None

        if s == 'periscope':
            assert S.streams[s].video_kbps == periscope_kbps
        else:
            assert S.streams[s].video_kbps == 400


@pytest.mark.timeout(TIMEOUT)
@pytest.mark.skipif(CI, reason='CI has no audio hardware typically')
def test_simple():
    """stream to localhost
    """
    S = pls.FileIn(inifn=None, websites='localhost',
                   infn=R / 'orch_short.ogg',
                   image=LOGO,
                   yes=True, timeout=5)

    S.golive()


@pytest.mark.skipif(CI, reason='CI has no audio hardware typically')
def test_script():
    subprocess.check_call([sys.executable, 'Glob.py',
                           str(VIDFN),
                           'localhost',
                           '--yes', '--timeout', '5'],
                          timeout=TIMEOUT, cwd=R.parent)


if __name__ == '__main__':
    pytest.main([__file__])
