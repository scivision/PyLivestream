#!/bin/sh

set -u

YOURSTREAM=$1

ffmpeg \
-f alsa -ac 1 -i hw:1,0 \
-f v4l2 -r 10 -i /dev/video0 \
-vcodec libx264 -pix_fmt yuv420p -preset ultrafast -g 20 -b:v 2500k \
-acodec libmp3lame -ar 44100 \
-threads 0 -bufsize 512k \
-f flv rtmp://a.rtmp.youtube.com/live2/$YOURSTREAM &> stream.log
