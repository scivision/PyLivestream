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
From PyPi::

    python -m pip install YouTubeLiveFFmpeg

Or for the latest copy from Github::

    python -m pip install -e .
    
    
Usage
=====
In all cases, you must first `configure YouTube Live <https://www.youtube.com/live_dashboard>`_.
Then your chosen input will stream live on YouTube Live.

Webcam
------
Audio is included::

    python Webcam2YouTubeLive.py
    
    
Screen Share
------------
Audio is included::

    python Screenshare2YouTubeLive.py
    
-fps      set frames/second
-res      set resolution XxY of your screen
-o        set origin (upper left)


Several video files
-------------------
Glob list of video files to stream::

    python FileGlob2YouTubeLive.py path pattern
    
path      path to where video files are
pattern   e.g. "*.avi"  pattern matching video files

e.g. stream all .avi video under ``~/Videos`` directory::

    python FileGlob2YouTubeLive.py ~/Videos "*.avi"



Several audio files
-------------------
Glob list of video files to stream. Note you must include a static image (could be your logo)::

    python FileGlob2YouTubeLive.py path pattern -i image
    
path      path to where video files are
pattern   e.g. "*.avi"  pattern matching video files
-i        filename of image to use as stream background

e.g. stream all .mp3 audio under ``~/Library`` directory::

    python FileGlob2YouTubeLive.py ~/Library "*.mp3" -i mylogo.jpg


Loop single video endlessly
---------------------------
::

    FileLoop2YouTubeLive.py videofile


Screen capture to disk
----------------------
This is NOT streaming, just saves to a file on your disk, perhaps for upload as a standard non-live YouTube video::

    python ScreenCapture2disk.py myvid.avi



Notes
=====

* FFmpeg Ubuntu `PPA <https://launchpad.net/~mc3man/+archive/ubuntu/trusty-media>`_
* `Reference webpage <https://www.scivision.co/youtube-live-ffmpeg-livestream/>`_
* `Test videos for looping/globbing <http://www.divx.com/en/devices/profiles/video>`_
* `FFmpeg streaming encoding reference <https://trac.ffmpeg.org/wiki/EncodingForStreamingSites>`_
