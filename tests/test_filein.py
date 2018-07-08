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

sites = ['periscope', 'youtube', 'facebook']
inifn = rdir/'test.ini'

VIDFN = rdir / 'bunny.avi'


def test_filein_video():
    S = pls.FileIn(inifn, sites, VIDFN)
    for s in S.streams:
        assert '-re' in S.streams[s].cmd
        assert S.streams[s].fps == 24.

        if s == 'periscope':
            assert S.streams[s].video_kbps == 800
        else:
            if int(S.streams[s].res[1]) == 480:
                assert S.streams[s].video_kbps == 500
            elif int(S.streams[s].res[1]) == 720:
                assert S.streams[s].video_kbps == 1800


def test_filein_audio():
    flist = list(rdir.glob('*.ogg'))

    S = pls.FileIn(inifn, sites, flist[0])
    for s in S.streams:
        assert '-re' in S.streams[s].cmd
        assert S.streams[s].fps is None

        if s == 'periscope':
            assert S.streams[s].video_kbps == 800
        else:
            assert S.streams[s].video_kbps == 500


@pytest.mark.skipif(CI, reason="Many CI's don't have audio hardware")
def test_file_simple():
    """stream to localhost"""
    s = pls.FileIn(inifn, 'localhost',
                   rdir / 'orch_short.ogg',
                   image=rdir.parent / 'doc' / 'logo.png',
                   yes=True)
    s.golive()


@pytest.mark.usefixtures("listener")
@pytest.mark.skipif(CI, reason="Many CI's don't have audio hardware")
def test_filein_script():
    subprocess.check_call(['FileGlobLivestream',
                           str(VIDFN),
                           'localhost-test',
                           '-i', str(inifn),
                           '--yes'],
                          stdout=DEVNULL, timeout=8,
                          cwd=rdir.parent)


if __name__ == '__main__':
    pytest.main()
