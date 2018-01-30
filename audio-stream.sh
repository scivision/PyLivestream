#!/bin/sh

ffmpeg -f alsa -ac 2 -i pulse -c:v aac -ar 8000 \
       -f rtp rtp://localhost:1234
