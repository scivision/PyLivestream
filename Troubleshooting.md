# Troubleshooting

Comments on dropouts / lag for livestreaming in general (not just with this program):

* Low CPU machines (like Raspberry Pi) may need to cut back on resolution.
* live streaming takes an excellent quality (not necessarily high speed) Internet connection in general. Some DSL / wireless internet provider have really spotty performance. You might not notice this with HD Netflix due to deep buffering, but it will show up on livestreaming.
* Do Skype / Duo / FaceTime work excellently for you on your network? If not, live streaming will not work well.
* Try a wired (Ethernet) connection to the Internet. I have seen very expensive consumer WiFi APs that had bad performance in real world strenuous use (like live streaming).

## Blank desktop sharing video.

In general since this program generates command lines that are run by FFmpeg, try just using FFmpeg by itself to write to a video file.
This is a known issue with Wayland--instead use X11.
See [FFmpeg Desktop capture docs](https://trac.ffmpeg.org/wiki/Capture/Desktop).

## YouTube stream health

Particularly when streaming with a static background `-image`, YouTube will often warn in "Stream Health":

> The stream's current bitrate is lower than the recommended bitrate.

Disregard this warning as long as your image looks OK.
