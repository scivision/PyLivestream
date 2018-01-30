#!/bin/bash

set -u

YOURSTREAM=$1

ffmpeg \
-f alsa -ac 2 -i hw:1,0 \
-f x11grab -r 10 -s 1024x720 -i :0.0+0,24 \
-c:v libx264 -pix_fmt yuv420p -preset veryfast -g 20 -b:v 2500k \
-c:a aac -ar 44100 \
-threads 0 -bufsize 512k \
-f flv rtmp://a.rtmp.youtube.com/live2/$YOURSTREAM &> stream.log
