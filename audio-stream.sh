#!/bin/sh

ffmpeg -f alsa -ac 2 -i pulse -acodec mp3 -ar 8000 \
       -f rtp rtp://localhost:1234
