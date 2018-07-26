#!/usr/bin/env python
from pathlib import Path
import PyLivestream as pls
import pytest
import os
import subprocess
from PyLivestream.listener import listener  # noqa: F401

CI = bool(os.environ['CI']) if 'CI' in os.environ else False
R = Path(__file__).resolve().parent  # .resolve() is necessary
DEVNULL = subprocess.DEVNULL

sites = ['periscope', 'youtube', 'facebook']
inifn = R / 'test.ini'
IMGFN = R.parent / 'doc' / 'logo.png'


def test_microphone():
    S = pls.Microphone(inifn, sites,
                       image=IMGFN)

    for s in S.streams:
        assert '-re' not in S.streams[s].cmd
        assert S.streams[s].fps is None

        if s == 'periscope':
            assert S.streams[s].video_kbps == 800
        else:
            assert S.streams[s].video_kbps == 500


@pytest.mark.usefixtures("listener")
@pytest.mark.skipif(CI, reason="Many CI's don't have audio hardware")
def test_microphone_stream():
    S = pls.Microphone(inifn, 'localhost-test', image=IMGFN)
    print('press   q   in terminal to proceed')
    S.golive()


@pytest.mark.usefixtures("listener")
@pytest.mark.skipif(CI, reason="Many CI's don't have audio hardware")
def test_microphone_script():
    subprocess.check_call(['MicrophoneLivestream',
                           '-i', str(inifn),
                           'localhost-test', '--yes'],
                          stdout=DEVNULL, timeout=8,
                          cwd=R.parent)


if __name__ == '__main__':
    pytest.main()
