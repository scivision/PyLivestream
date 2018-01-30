#!/bin/bash

# sends your webcam video to YouTube Live stream.

set -u

YOURSTREAM=$1
VDEV=/dev/video0

ffmpeg \
-f alsa -ac 2 -i hw:1,0 \
-f v4l2 -r 30 -i $VDEV \
-c:v libx264 -pix_fmt yuv420p -preset veryfast -g 20 -b:v 2500k \
-c:a aac -ar 44100 \
-threads 0 -bufsize 512k \
-f flv rtmp://a.rtmp.youtube.com/live2/$YOURSTREAM &> stream.log
