#!/bin/sh

set -u

outfn=$1

ffmpeg \
-video_size 1024x720 \
-framerate 10 \
-f x11grab -i :0.0+100,200 \
-f pulse -ac 2 -i default \
-c:a aac -ar 48000 \
$outfn
