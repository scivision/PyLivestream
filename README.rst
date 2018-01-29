.. image:: https://travis-ci.org/scivision/ffmpeg-youtube-live.svg?branch=master
    :target: https://travis-ci.org/scivision/ffmpeg-youtube-live

.. image:: https://coveralls.io/repos/github/scivision/ffmpeg-youtube-live/badge.svg?branch=master
    :target: https://coveralls.io/github/scivision/ffmpeg-youtube-live?branch=master

.. image:: https://img.shields.io/pypi/pyversions/youtubeliveffmpeg.svg
  :target: https://pypi.python.org/pypi/youtubeliveffmpeg
  :alt: Python versions (PyPI)

.. image::  https://img.shields.io/pypi/format/youtubeliveffmpeg.svg
  :target: https://pypi.python.org/pypi/youtubeliveffmpeg
  :alt: Distribution format (PyPI)

.. image:: https://api.codeclimate.com/v1/badges/b6557d474ec050e74629/maintainability
   :target: https://codeclimate.com/github/scivision/ffmpeg-youtube-live/maintainability
   :alt: Maintainability

========================
YouTube Live via FFmpeg
========================

FFmpeg can easily be used to stream to YouTube Live for streaming broadcasts.
These Python scripts compute the optimal parameters.
Should work on any OS (Mac, Linux, Windows).

:Linux: requires X11, not Wayland (choose at login)
:FFmpeg: >= 3.0 required
:Python: >= 3.6 required


.. contents::

Install
=======
::

    python -m pip install -e .


Usage
=====

Specify your video/audio device if desired at the top of the script.
Find device names with commands like:

* Windows: ``ffmpeg -list_devices true -f dshow -i dummy``
* Mac: ``ffmpeg -f avfoundation -list_devices true -i ""``
* Linux: ``v4l2-ctl --list-devices``

I will describe usage for each of YouTube Live, Facebook Live, and Periscope.

YouTube Live
------------

1. `configure  <https://www.youtube.com/live_dashboard>`_ YouTube Live.
2. Run Python script and chosen input will stream on YouTube Live.


Webcam
~~~~~~
Audio is included::

    python Webcam2YouTubeLive.py


Screen Share
~~~~~~~~~~~~
Audio is included::

    python Screenshare2YouTubeLive.py

-fps      set frames/second
-res      set resolution XxY of your screen
-o        set origin (upper left)


several video files
~~~~~~~~~~~~~~~~~~~
Glob list of video files to stream::

    python FileGlob2YouTubeLive.py path pattern

-loop       optionally loop endlessly the globbed file list


stream all videos in directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Example: all AVI videos in directory ``~/Videos``::

    python FileGlob2YouTubeLive.py ~/Videos "*.avi"

stream endlessly looping videos
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Example: all AVI videos in ``~/Videos`` are endlessly looped::

    python FileGlob2YouTubeLive.py ~/Videos "*.avi" -loop


stream all audio files in directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Glob list of video files to stream. 
Must include a static image (could be your logo)::

    python FileGlob2YouTubeLive.py path pattern -i image

path      path to where video files are
pattern   e.g. "*.avi"  pattern matching video files
-i        filename of image to use as stream background

Example: stream all .mp3 audio under ``~/Library`` directory::

    python FileGlob2YouTubeLive.py ~/Library "*.mp3" -i mylogo.jpg


Loop single video endlessly
~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    FileLoop2YouTubeLive.py videofile


Screen capture to disk
----------------------
This is NOT streaming.
This script saves your screen capture to a file on your disk::

    python ScreenCapture2disk.py myvid.avi


Facebook Live
-------------

1. configure your Facebook Live stream, get stream ID from `https://www.facebook.com/live/create <https://www.facebook.com/live/create>`_
2. Run Python script for Facebook with chosen input

::

    python Screenshare2FacebookLive.py
    
    
Periscope
---------

1. create a new stream by EITHER:

   * from phone Periscope app, go to Profile -> Settings -> Periscope Producer and see your Stream Key. The "checking source" button will go to "preview stream" once you do step #2.
   * from computer web browser, go to `https://www.periscope.tv/account/producer <https://www.periscope.tv/account/producer>`_ and Create New Source.
2. Run Python script for Periscope with chosen input

::

    python Screenshare2Periscope.py
    
    
I prefer using the Phone method as then the phone is a "second screen" where I can see if the stream is lagging, and if I "leave broadcast" and come back in, I can comment from my phone etc.

Notes
=====

* FFmpeg Ubuntu `PPA <https://launchpad.net/~mc3man/+archive/ubuntu/trusty-media>`_
* `Reference webpage <https://www.scivision.co/youtube-live-ffmpeg-livestream/>`_
* `Test videos for looping/globbing <http://www.divx.com/en/devices/profiles/video>`_

FFmpeg References
-----------------

* `streaming <https://trac.ffmpeg.org/wiki/EncodingForStreamingSites>`_
* `webcam <https://trac.ffmpeg.org/wiki/Capture/Webcam>`_

Windows
~~~~~~~
* `DirectShow <https://trac.ffmpeg.org/wiki/DirectShow>`_ device selection
* DirectShow `examples <https://ffmpeg.org/ffmpeg-devices.html#Examples-4>`_
