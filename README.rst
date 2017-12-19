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
:Python: >= 3.5 required

Install
=======
From PyPi::

    python -m pip install YouTubeLiveFFmpeg

Or for the latest copy from Github::

    python -m pip install -e .


Notes
=====

* FFmpeg Ubuntu `PPA <https://launchpad.net/~mc3man/+archive/ubuntu/trusty-media>`_
* `Reference webpage <https://www.scivision.co/youtube-live-ffmpeg-livestream/>`_
* `Test videos for looping/globbing <http://www.divx.com/en/devices/profiles/video>`_
* `FFmpeg streaming encoding reference <https://trac.ffmpeg.org/wiki/EncodingForStreamingSites>`_
