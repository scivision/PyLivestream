#!/usr/bin/env python
from pathlib import Path
import PyLivestream

rdir = Path(__file__).parents[1]

inifn = rdir / 'stream.ini'

P = {'ini': inifn, 'vidsource': 'file', 'site': 'file'}

PyLivestream.disksave(P)
