#!/usr/bin/env python3

"""
Use a playlist to stream files from m3u8: https://github.com/globocom/m3u8

    pip install m3u8

Example from Akamai:

https://learn.akamai.com/en-us/webhelp/media-services-live/media-services-live-4-user-guide/GUID-0A50253F-0B1B-406B-A8C9-3788CB42F950.html
"""

from pathlib import Path
import pylivestream.api as pls

import m3u8

playlist_m3u8 = Path(__file__).parent / "local.m3u8"

playlist = m3u8.load(str(playlist_m3u8))

files = playlist.files

for file in files:
    pls.stream_file(
        ini_file=None,
        websites="localhost",
        assume_yes=True,
        video_file=file,
    )
