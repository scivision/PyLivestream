#!/usr/bin/env python
from pathlib import Path
import pylivestream as pls
import pytest
from pytest import approx
import subprocess

R = Path(__file__).parent

sites = ['periscope', 'youtube', 'facebook']
inifn = R / 'test.ini'

VIDFN = R / 'bunny.avi'
LOGO = R.parent / 'doc' / 'logo.png'

S = pls.stream.Stream(inifn, 'localhost-test')
S.osparam()
timelimit = int(S.timelimit[1]) + 3   # allowing 3 seconds leeway
del S


def test_filein_video():
    S = pls.FileIn(inifn, sites, VIDFN)
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


def test_filein_audio():
    flist = list(R.glob('*.ogg'))

    S = pls.FileIn(inifn, sites, flist[0], image=LOGO)
    for s in S.streams:
        assert '-re' in S.streams[s].cmd
        assert S.streams[s].fps is None

        if s == 'periscope':
            assert S.streams[s].video_kbps == 800
        else:
            assert S.streams[s].video_kbps == 400


def test_file_simple():
    """stream to localhost
    no listener fixture, to test the other listener
    """
    # not localhost-test, to test the other listener
    S = pls.FileIn(inifn, 'localhost',
                   R / 'orch_short.ogg',
                   image=LOGO,
                   yes=True)

    S.golive()


def test_filein_script(listener):
    subprocess.check_call(['FileGlobLivestream',
                           str(VIDFN),
                           'localhost-test',
                           '-i', str(inifn),
                           '--yes'],
                          timeout=timelimit)


if __name__ == '__main__':
    pytest.main(['-x', __file__])
