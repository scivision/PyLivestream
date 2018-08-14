#!/usr/bin/env python
"""
plays several tests to localhost for testing.

"bunny" clip created by:

ffmpeg -ss 00:00:30 -i BigBuckBunny_DivX_HD720p_ASP.divx -t 7 -vf scale=-2:240 -c:v libx264 -c:a aac bunny.avi
"""
from pathlib import Path
import subprocess

R = Path(__file__).parent
VIDPATH = R / 'tests'
IMGPATH = R / 'doc'
HOST = 'localhost'
STATIC = IMGPATH / 'logo.png'
MOVING = VIDPATH / 'cc_land.gif'
VIDEO = VIDPATH / 'bunny.avi'
MUSIC = VIDPATH / 'orch.ogg'


def main():
    print('these tests enable a user to visually confirm PyLiveStream code is working.')
    print('the streaming is just on your own computer.')
    print('\n\n press   q   in the terminal window to proceed to the next test. \n\n')

    # %% Microphone
    print('PyLivestream splash with live microphone audio')
    subprocess.check_call(['MicrophoneLivestream', '-y',  HOST, '-image', str(STATIC)])

    print('1990s vector graphics with live microphone audio')
    subprocess.check_call(['MicrophoneLivestream', '-y',  HOST, '-image', str(MOVING)])
    # %%  Music
    print('PyLivestream splash with orchestra music  (caption)')
    subprocess.check_call(['FileGlobLivestream', '-y',  '-image', str(STATIC),
                           str(VIDPATH), HOST,
                           '-glob', 'orch.ogg'])

    print('1990s vector graphics with orchestra music (NO caption')
    subprocess.check_call(['FileGlobLivestream', '-y', '-image', str(MOVING),
                           str(MUSIC), HOST])
    # video
    print('Looping video')
    subprocess.check_call(['FileGlobLivestream', '-y',
                           str(VIDEO), HOST])
    # %% Screenshare
    print('Screenshare + microphone')
    subprocess.check_call(['ScreenshareLivestream', '-y',  HOST])
    # %% loop video
    print('Looping video')
    subprocess.check_call(['FileLoopLivestream', '-y',  str(VIDEO), HOST])
    # %% Webcam
    print('Webcam test - will fail if no webcam present on your system')
    subprocess.check_call(['WebcamLivestream', '-y', HOST])


if __name__ == '__main__':
    main()
