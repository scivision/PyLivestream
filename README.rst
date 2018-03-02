.. image:: https://travis-ci.org/scivision/PyLivestream.svg?branch=master
    :target: https://travis-ci.org/scivision/PyLivestream

.. image:: https://coveralls.io/repos/github/scivision/PyLivestream/badge.svg?branch=master
    :target: https://coveralls.io/github/scivision/PyLivestream?branch=master

.. image:: https://img.shields.io/pypi/pyversions/PyLivestream.svg
  :target: https://pypi.python.org/pypi/PyLivestream
  :alt: Python versions (PyPI)

.. image::  https://img.shields.io/pypi/format/PyLivestream.svg
  :target: https://pypi.python.org/pypi/PyLivestream
  :alt: Distribution format (PyPI)

.. image:: https://api.codeclimate.com/v1/badges/b6557d474ec050e74629/maintainability
   :target: https://codeclimate.com/github/scivision/ffmpeg-youtube-live/maintainability
   :alt: Maintainability

==========================================
Python scripted livestreaming using FFmpeg
==========================================

Streams to one or **multiple** streaming sites simultaneously.
FFmpeg is used from Python ``subprocess`` to stream to Facebook Live, YouTube Live, Periscope, Twitch, Mixer, Ustream, Vimeo and more for streaming broadcasts.
The Python scripts compute good streaming parameters, and emit the command used so you can just copy and paste in the future if you wish.
Works on any OS (Mac, Linux, Windows).
Uses an ``.ini`` file to adjust all parameters.

.. image:: doc/logo.png
   :alt: PyLivestream diagram showing screen capture or webcam simultaneously livestreaming to multiple services.


:FFmpeg: >= 3.0 required
:Python: >= 3.5 required


.. contents::

Install
=======
::

    python -m pip install -e .


Configuration
=============
You can skip past this section to "stream start" if it's confusing.
The defaults might work to get you started.


The ``stream.ini`` file contains parameters relevant to your stream.
The ``[DEFAULT]`` section has parameters that can be overriden for each site, if desired.

* ``screencap_origin``: origin (upper left corner) of screen capture region in pixels.
* ``screencap_res``: resolution of screen capture (area to capture, starting from origin)
* ``screencap_fps``: frames/sec of screen capture
* ``webcam_res``: webcam resolution -- find from ``v4l2-ctl --list-formats-ext`` or webcam spec sheet.
* ``webcam_fps``: webcam fps -- found from command above or webcam spec sheet
* ``audiofs``: audio sampling frequency. Typically 44100 Hz (CD quality).
* ``audio_bps``: audio data rate--**leave blank if you want no audio** (usually used for "file", to make an animated GIF in post-processing)
* ``preset``: ``veryfast`` or ``ultrafast`` if CPU not able to keep up.


Next are ``sys.platform`` specific parameters.
Find webcam name by:

* Windows: ``ffmpeg -list_devices true -f dshow -i dummy``
* Mac: ``ffmpeg -f avfoundation -list_devices true -i ""``
* Linux: ``v4l2-ctl --list-devices``

Seek help in FFmpeg documentation, try capturing to a file first and then update ``stream.ini`` for your ``sys.platform``.

* ``exe``: override path to desired FFmpeg executable. In case you have multiple FFmpeg versions installed (say, from Anaconda Python).

Finally are the per-site parameters.
The only thing you would possibly need to change here is the ``server`` for best performance for your geographic region.
The included ``stream.ini`` is with default servers for the Northeastern USA.


Stream Start
============

YouTube Live
------------

1. `configure  <https://www.youtube.com/live_dashboard>`_ YouTube Live.
2. Run Python script and chosen input will stream on YouTube Live.

::

    python ScreenshareLivestream.py stream.ini youtube


Facebook Live
-------------

1. configure your Facebook Live stream, get stream ID from `https://www.facebook.com/live/create <https://www.facebook.com/live/create>`_
2. Run Python script for Facebook with chosen input

::

    python ScreenshareLivestream.py stream.ini facebook


Periscope
---------

1. create a new stream by EITHER:

   * from phone Periscope app, go to Profile -> Settings -> Periscope Producer and see your Stream Key. The "checking source" button will go to "preview stream" once you do step #2.
   * from computer web browser, go to `https://www.periscope.tv/account/producer <https://www.periscope.tv/account/producer>`_ and Create New Source.
2. Run Python script for Periscope with chosen input

::

    python ScreenshareLivestream.py stream.ini periscope

I prefer using the Phone method as then the phone is a "second screen" where I can see if the stream is lagging, and if I "leave broadcast" and come back in, I can comment from my phone etc.


Twitch
------

1. create stream from `Twitch Dashboard <http://www.twitch.tv/broadcast/dashboard>`_
2. Run Python script for Twitch with chosen input

If you are not in the Northeast US, edit `stream.ini` to have the `closest server <http://bashtech.net/twitch/ingest.php>`_.


Usage
=====

Due to the complexity of streaming and the non-specific error codes FFmpeg emits,
the default behavior is that if FFmpeg detects one stream has failed, ALL streams will stop streaming and the program ends.


* ``stream.ini`` is setup for your computer and desired parameters
* ``site`` is ``facebook``, ``periscope``, ``youtube``, etc.
* For ``Webcam.py`` and ``Screenshare.py``, more than one ``site`` can be specified for simultaneous multi-streaming



Webcam
------
Audio is included::

    python WebcamLivestream.py stream.ini site(s)

Stream to multiple sites, in this example Periscope and YouTube Live simultaneously::

    python WebcamLivestream.py stream.ini youtube periscope



Screen Share Livestream
-----------------------
Audio is included::

    python ScreenshareLivestream.py stream.ini site(s)

Stream to multiple sites, in this example Periscope and YouTube Live simultaneously::

    python ScreenshareLivestream.py stream.ini youtube periscope


File Input
----------


Loop single video endlessly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    python FileLoopLivestream.py stream.ini site videofile


several video files
~~~~~~~~~~~~~~~~~~~
Glob list of video files to stream::

    python FileGlobLivestream.py stream.ini site path pattern

-loop       optionally loop endlessly the globbed file list


stream all videos in directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Example: all AVI videos in directory ``~/Videos``::

    python FileGlobLivestream.py stream.ini youtube ~/Videos "*.avi"

stream endlessly looping videos
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Example: all AVI videos in ``~/Videos`` are endlessly looped::

    python FileGlobLivestream.py stream.ini youtube ~/Videos "*.avi" -loop


stream all audio files in directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Glob list of video files to stream.
Must include a static image (could be your logo)::

    python FileGlobLivestream.py stream.ini site path pattern -i image

path      path to where video files are
pattern   e.g. ``*.avi``  pattern matching video files
-i        filename of image to use as stream background

Example: stream all .mp3 audio under ``~/Library`` directory::

    python FileGlobLivestream.py stream.ini youtube ~/Library "*.mp3" -i mylogo.jpg


Screen capture to disk
----------------------
This script saves your screen capture to a file on your disk::

    python ScreenCapture2disk.py stream.ini myvid.avi



Utilities
=========

* ``PyLivestream.get_framerate(vidfn)`` gives the frames/sec of a video file.
* ``PyLivestream.get_resolution(vidfn)`` gives the resolution (widthxheight) of video file.


Notes
=====

* Linux requires X11, not Wayland (choose at login)
* ``x11grab`` was deprecated in FFmpeg 3.3, was previously replaced by ``xcbgrab``
* Reference `webpage <https://www.scivision.co/youtube-live-ffmpeg-livestream/>`_
* `Test videos <http://www.divx.com/en/devices/profiles/video>`_ for looping/globbing

FFmpeg References
-----------------

* `streaming <https://trac.ffmpeg.org/wiki/EncodingForStreamingSites>`_
* `webcam <https://trac.ffmpeg.org/wiki/Capture/Webcam>`_
* webcam `overlay <https://trac.ffmpeg.org/wiki/EncodingForStreamingSites#Withwebcamoverlay>`_

Windows
~~~~~~~

* `gdigrab <https://ffmpeg.org/ffmpeg-devices.html#gdigrab>`_

DirectShow didn't work for me on Windows 10, so I used gdigrab instead.
* `DirectShow <https://trac.ffmpeg.org/wiki/DirectShow>`_ device selection
* DirectShow `examples <https://ffmpeg.org/ffmpeg-devices.html#Examples-4>`_

Stream References
-----------------

* Twitch `parameters <https://help.twitch.tv/customer/portal/articles/1253460-broadcast-requirements>`_
* Twitch `servers <http://bashtech.net/twitch/ingest.php>`_
* Periscope `parameters <https://www.pscp.tv/help/external-encoders>`_
* YouTube Live `parameters <https://support.google.com/youtube/answer/2853702>`_
* Facebook Live `parameters <https://www.facebook.com/facebookmedia/get-started/live>`_
* Mixer `parameters <https://watchbeam.zendesk.com/hc/en-us/articles/210090606-Stream-Settings-the-basics>`_
* Mixer `server list <https://watchbeam.zendesk.com/hc/en-us/articles/209659883-How-to-change-your-Ingest-Server>`_
* Ustream `parameters <https://support.ustream.tv/hc/en-us/articles/207852117-Internet-connection-and-recommended-encoding-settings>`_
* Vimeo `config <https://help.vimeo.com/hc/en-us/articles/115012811168>`_
* Vimeo `parameters <https://help.vimeo.com/hc/en-us/articles/115012811208-Encoder-guides>`_


Logo Credits:
------------
* Owl PC: Creative Commons no attrib. commercial
* YouTube: YouTube Brand Resources
* Facebook: Wikimedia Commons
* `Periscope <periscope.tv/press>`_
