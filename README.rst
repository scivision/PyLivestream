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

Linux: requires X11, not Wayland (choose at login)

Install
=======
From PyPi::

    python -m pip install YouTubeLiveFFmpeg

Or for the latest copy from Github::

    python -m pip install -e .


Prereq
------
* FFmpeg
* Python (just for scripting)

Note: for FileLoop2YouTubeLive.py, FFmpeg >= 3 required.
If you're on Ubuntu, you can use a `PPA <https://launchpad.net/~mc3man/+archive/ubuntu/trusty-media>`_ to update your FFmpeg version.






Notes
=====

`Reference webpage <https://www.scivision.co/youtube-live-ffmpeg-livestream/>`_

