#!/usr/bin/env python
from pathlib import Path
import pylivestream as pls
import pytest
from pytest import approx
import subprocess
import os

R = Path(__file__).parent

sites = ['periscope', 'youtube', 'facebook']
inifn = R.parent / 'stream.ini'

VIDFN = R / 'bunny.avi'
LOGO = R.parent / 'doc' / 'logo.png'
TIMEOUT = 30

CI = os.environ.get('CI', None) in ('true', 'True')


def test_props():
    S = pls.FileIn(inifn, sites, infn=VIDFN)
    for s in S.streams:
        assert '-re' in S.streams[s].cmd
        assert S.streams[s].fps == approx(24.)

        if s == 'periscope':
            assert S.streams[s].video_kbps == 800
        else:
            if int(S.streams[s].res[1]) == 480:
                assert S.streams[s].video_kbps == 500
            elif int(S.streams[s].res[1]) == 720:
                assert S.streams[s].video_kbps == 1800


def test_audio():
    flist = list(R.glob('*.ogg'))

    S = pls.FileIn(inifn, sites, infn=flist[0], image=LOGO)
    for s in S.streams:
        assert '-re' in S.streams[s].cmd
        assert S.streams[s].fps is None

        if s == 'periscope':
            assert S.streams[s].video_kbps == 800
        else:
            assert S.streams[s].video_kbps == 400


@pytest.mark.timeout(TIMEOUT)
@pytest.mark.skipif(CI, reason='CI has no audio hardware typically')
def test_simple():
    """stream to localhost
    """
    S = pls.FileIn(inifn, 'localhost',
                   infn=R / 'orch_short.ogg',
                   image=LOGO,
                   yes=True, timeout=5)

    S.golive()


@pytest.mark.skipif(CI, reason='CI has no audio hardware typically')
def test_script():
    subprocess.check_call(['FileGlobLivestream',
                           str(VIDFN),
                           'localhost',
                           '-i', str(inifn),
                           '--yes', '--timeout', '5'],
                          timeout=TIMEOUT)


if __name__ == '__main__':
    pytest.main(['-x', __file__])
