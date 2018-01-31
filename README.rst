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

:FFmpeg: >= 3.0 required
:Python: >= 3.5 required


.. contents::

Install
=======
::

    python -m pip install -e .


Stream Setup
============

The ``.ini`` file contains parameters relevant to your stream.
Find device names with commands like:

* Windows: ``ffmpeg -list_devices true -f dshow -i dummy``
* Mac: ``ffmpeg -f avfoundation -list_devices true -i ""``
* Linux: ``v4l2-ctl --list-devices``

I will describe usage for each of YouTube Live, Facebook Live, Periscope and Twitch.

YouTube Live
------------

1. `configure  <https://www.youtube.com/live_dashboard>`_ YouTube Live.
2. Run Python script and chosen input will stream on YouTube Live.

::

    python Screenshare.py stream.ini youtube


Facebook Live
-------------

1. configure your Facebook Live stream, get stream ID from `https://www.facebook.com/live/create <https://www.facebook.com/live/create>`_
2. Run Python script for Facebook with chosen input

::

    python Screenshare.py stream.ini facebook


Periscope
---------

1. create a new stream by EITHER:

   * from phone Periscope app, go to Profile -> Settings -> Periscope Producer and see your Stream Key. The "checking source" button will go to "preview stream" once you do step #2.
   * from computer web browser, go to `https://www.periscope.tv/account/producer <https://www.periscope.tv/account/producer>`_ and Create New Source.
2. Run Python script for Periscope with chosen input

::

    python Screenshare.py stream.ini periscope

I prefer using the Phone method as then the phone is a "second screen" where I can see if the stream is lagging, and if I "leave broadcast" and come back in, I can comment from my phone etc.


Twitch
------

1. create stream from `Twitch Dashboard <http://www.twitch.tv/broadcast/dashboard>`_
2. Run Python script for Twitch with chosen input

If you are not in the Northeast US, edit `stream.ini` to have the `closest server <http://bashtech.net/twitch/ingest.php>`_.


Usage
=========

* ``stream.ini`` is setup for your computer and desired parameters
* ``site`` is ``facebook``, ``periscope`` or ``youtube``



Webcam
------
Audio is included::

    python Webcam.py stream.ini site


Screen Share Livestream
-----------------------
Audio is included::

    python Screenshare.py stream.ini site(s)

Stream to multiple sites, in this example Periscope and YouTube Live simultaneously::

    python Screenshare.py stream.ini youtube periscope


File Input
----------


Loop single video endlessly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    python FileLoop.py stream.ini site videofile


several video files
~~~~~~~~~~~~~~~~~~~
Glob list of video files to stream::

    python FileGlob.py stream.ini site path pattern

-loop       optionally loop endlessly the globbed file list


stream all videos in directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Example: all AVI videos in directory ``~/Videos``::

    python FileGlob.py stream.ini youtube ~/Videos "*.avi"

stream endlessly looping videos
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Example: all AVI videos in ``~/Videos`` are endlessly looped::

    python FileGlob.py stream.ini youtube ~/Videos "*.avi" -loop


stream all audio files in directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Glob list of video files to stream.
Must include a static image (could be your logo)::

    python FileGlob.py stream.ini site path pattern -i image

path      path to where video files are
pattern   e.g. ``*.avi``  pattern matching video files
-i        filename of image to use as stream background

Example: stream all .mp3 audio under ``~/Library`` directory::

    python FileGlob.py stream.ini youtube ~/Library "*.mp3" -i mylogo.jpg


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
* FFmpeg Ubuntu `PPA <https://launchpad.net/~mc3man/+archive/ubuntu/trusty-media>`_
* `Reference webpage <https://www.scivision.co/youtube-live-ffmpeg-livestream/>`_
* `Test videos for looping/globbing <http://www.divx.com/en/devices/profiles/video>`_

FFmpeg References
-----------------

* `streaming <https://trac.ffmpeg.org/wiki/EncodingForStreamingSites>`_
* `webcam <https://trac.ffmpeg.org/wiki/Capture/Webcam>`_
* `webcam overlay <https://trac.ffmpeg.org/wiki/EncodingForStreamingSites#Withwebcamoverlay>`_

Windows
~~~~~~~
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
