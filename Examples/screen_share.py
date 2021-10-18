#!/usr/bin/env python3
"""
example of screen sharing to livestream
"""

import pylivestream.api as pls

pls.stream_screen(ini_file=None, websites="localhost", assume_yes=True)
