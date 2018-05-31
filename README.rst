.. image:: https://travis-ci.org/scivision/PyLivestream.svg?branch=master
    :target: https://travis-ci.org/scivision/PyLivestream

.. image:: https://coveralls.io/repos/github/scivision/PyLivestream/badge.svg?branch=master
    :target: https://coveralls.io/github/scivision/PyLivestream?branch=master

.. image:: https://ci.appveyor.com/api/projects/status/uwhsko29b1g5c3no?svg=true
    :target: https://ci.appveyor.com/project/scivision/pylivestream

.. image:: https://img.shields.io/pypi/pyversions/PyLivestream.svg
  :target: https://pypi.python.org/pypi/PyLivestream
  :alt: Python versions (PyPi)

.. image::  https://img.shields.io/pypi/format/PyLivestream.svg
  :target: https://pypi.python.org/pypi/PyLivestream
  :alt: Distribution format (PyPi)

.. image:: https://api.codeclimate.com/v1/badges/b6557d474ec050e74629/maintainability
   :target: https://codeclimate.com/github/scivision/ffmpeg-youtube-live/maintainability
   :alt: Maintainability

==========================================
Python scripted livestreaming using FFmpeg
==========================================

Streams to one or **multiple** streaming sites simultaneously.
FFmpeg is used from Python ``subprocess`` to stream to Facebook Live, YouTube Live, Periscope, Twitch, Mixer, Ustream, Vimeo and more for streaming broadcasts.
The Python scripts compute good streaming parameters, and emit the command used so you can just copy and paste in the future if you wish.
Works on any OS (Mac, Linux, Windows) and computing platform, including PC, Mac, and Raspberry Pi.
Uses an ``.ini`` file to adjust all parameters.

.. image:: doc/logo.png
   :alt: PyLivestream diagram showing screen capture or webcam simultaneously livestreaming to multiple services.


:FFmpeg: >= 3.0 required
:Python: >= 3.6 required

Caveats
=======

Comments on dropouts / lag for livestreaming in general (not just with this program):

* live streaming takes full CPU power in general. Low CPU machines (like Raspberry Pi) will need to cut back on resolution. Try starting at 240p (320x240) and working your way up if you have dropouts.
* live streaming takes an excellent quality (not necessarily high speed) Internet connection in general. Some DSL / wireless internet provider have really spotty performance. You might not notice this with HD Netflix due to deep buffering, but it will show up on livestreaming.
* Do Skype / Duo / FaceTime work excellently for you on your network? If not, live streaming will not work well.
* Try a wired (Ethernet) connection to the Internet. I have seen very expensive consumer WiFi APs that just had bad performance in real world strenuous use (like live streaming).

.. contents::

Install
=======

Latest release::

    python -m pip install PyLivestream

Development version::

    git clone https://github.com/scivision/PyLivestream

    cd PyLivestream

    python -m pip install -e .


Configuration
=============
You can skip past this section to "stream start" if it's confusing.
The defaults might work to get you started.


The ``stream.ini`` file contains parameters relevant to your stream.
The ``[DEFAULT]`` section has parameters that can be overridden for each site, if desired.

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

The program will load a ``*.key`` file according to the configuration file key for the website.
For example, Periscope expects to see the stream hexadecimal key in ``periscope.key``, as obtained from the app.
Likewise, YouTube expects a file ``youtube.key`` with the hexadecimal stream key and so on.

YouTube Live
------------

1. `configure  <https://www.youtube.com/live_dashboard>`_ YouTube Live.
2. Edit file ``youtube.key`` to have the YouTube hexadecimal stream key
3. Run Python script and chosen input will stream on YouTube Live.

::

    python ScreenshareLivestream.py youtube


Facebook Live
-------------

1. configure your Facebook Live stream
2. Put stream ID from `https://www.facebook.com/live/create <https://www.facebook.com/live/create>`_  into the file ``facebook.key``
3. Run Python script for Facebook with chosen input

::

    python ScreenshareLivestream.py facebook


Periscope
---------

1. create a new stream by EITHER:

   * from phone Periscope app, go to Profile -> Settings -> Periscope Producer and see your Stream Key. The "checking source" button will go to "preview stream" once you do step #2.
   * from computer web browser, go to `https://www.periscope.tv/account/producer <https://www.periscope.tv/account/producer>`_ and Create New Source.
2. Put the hexadecimal stream key into ``periscope.key``
3. Run Python script for Periscope with chosen input

::

    python ScreenshareLivestream.py periscope

I prefer using the Phone method as then the phone is a "second screen" where I can see if the stream is lagging, and if I "leave broadcast" and come back in, I can comment from my phone etc.


Twitch
------

1. create stream from `Twitch Dashboard <http://www.twitch.tv/broadcast/dashboard>`_. If you are not in the Northeast US, edit ``stream.ini`` to have the `closest server <http://bashtech.net/twitch/ingest.php>`_.
2. put Twitch stream key into file ``twitch.key``
3. Run Python script for Twitch with chosen input


::

    python ScreenshareLivestream.py twitch


Usage
=====

Due to the complexity of streaming and the non-specific error codes FFmpeg emits,
the default behavior is that if FFmpeg detects one stream has failed, ALL streams will stop streaming and the program ends.


* ``stream.ini`` is setup for your computer and desired parameters
* ``site`` is ``facebook``, ``periscope``, ``youtube``, etc.
* For ``Webcam.py`` and ``Screenshare.py``, more than one ``site`` can be specified for simultaneous multi-streaming
* remember to setup a ``*.key`` file with the hexadecimal stream key for EACH site first, OR input the stream key into the "key:" field of your ``*.ini`` file.


Webcam
------
Audio is included::

    python WebcamLivestream.py site(s)

Stream to multiple sites, in this example Periscope and YouTube Live simultaneously::

    python WebcamLivestream.py youtube periscope



Screen Share Livestream
-----------------------
Audio is included::

    python ScreenshareLivestream.py site(s)

Stream to multiple sites, in this example Periscope and YouTube Live simultaneously::

    python ScreenshareLivestream.py youtube periscope


File Input
----------


Loop single video endlessly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    python FileLoopLivestream.py site videofile


several video files
~~~~~~~~~~~~~~~~~~~
Glob list of video files to stream::

    python FileGlobLivestream.py site path pattern

-loop       optionally loop endlessly the globbed file list
-image      if you have AUDIO files, you should normally set an image to display, as most/all streaming sites REQUIRE a video feed--even a static image.


stream all videos in directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Example: all AVI videos in directory ``~/Videos``::

    python FileGlobLivestream.py youtube ~/Videos "*.avi"

stream endlessly looping videos
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Example: all AVI videos in ``~/Videos`` are endlessly looped::

    python FileGlobLivestream.py youtube ~/Videos "*.avi" -loop


stream all audio files in directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Glob list of video files to stream.
Must include a static image (could be your logo)::

    python FileGlobLivestream.py site path pattern -image image

path      path to where video files are
pattern   e.g. ``*.avi``  pattern matching video files
-image        filename of image to use as stream background (REQUIRED for most websites)

Example: stream all .mp3 audio under ``~/Library`` directory::

    python FileGlobLivestream.py youtube ~/Library "*.mp3" -image mylogo.jpg


Screen capture to disk
----------------------
This script saves your screen capture to a file on your disk::

    python ScreenCapture2disk.py myvid.avi



Utilities
=========

* ``PyLivestream.get_framerate(vidfn)`` gives the frames/sec of a video file.
* ``PyLivestream.get_resolution(vidfn)`` gives the resolution (width x height) of video file.


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

* `Twitch parameters <https://help.twitch.tv/customer/portal/articles/1253460-broadcast-requirements>`_
* Twitch `servers <http://bashtech.net/twitch/ingest.php>`_
* `Periscope parameters <https://www.pscp.tv/help/external-encoders>`_
* `YouTube Live parameters <https://support.google.com/youtube/answer/2853702>`_
* `Facebook Live parameters <https://www.facebook.com/facebookmedia/get-started/live>`_
* `Mixer parameters <https://watchbeam.zendesk.com/hc/en-us/articles/210090606-Stream-Settings-the-basics>`_
* Mixer `server list <https://watchbeam.zendesk.com/hc/en-us/articles/209659883-How-to-change-your-Ingest-Server>`_
* `Ustream parameters <https://support.ustream.tv/hc/en-us/articles/207852117-Internet-connection-and-recommended-encoding-settings>`_
* Vimeo `config <https://help.vimeo.com/hc/en-us/articles/115012811168>`_
* Vimeo `parameters <https://help.vimeo.com/hc/en-us/articles/115012811208-Encoder-guides>`_


Logo Credits
-------------
* Owl PC: Creative Commons no attrib. commercial
* YouTube: YouTube Brand Resources
* Facebook: Wikimedia Commons
* `Periscope <periscope.tv/press>`_
