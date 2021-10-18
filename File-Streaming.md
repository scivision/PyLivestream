# File Livestream

Captions: if you have installed the optional `tinytag` Python module,
the Title - Artist will be added automatically onto the video from the
audio/video files.

## Loop single video endlessly

```sh
FileLoopLivestream videofile site
```

## several video files

Glob list of video files to stream:

```sh
FileGlobLivestream path site -glob glob_pattern
```

* `-glob` glob pattern of files to stream e.g. "*.avi".  For [recursive globbing](https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob), do like "**/*.avi".
* `-loop` optionally loop endlessly the globbed file list
* `-shuffle` optionally shuffle the globbed file list
* `-image` if you have AUDIO files, you should normally set an image to display, as most/all streaming sites REQUIRE a video feed--even a static image.
* `-nometa` disable Title - Artist text overlay

## stream all videos in directory

Example: all AVI videos in directory `~/Videos`:

```sh
FileGlobLivestream ~/Videos youtube -glob "*.avi"
```

## stream endlessly looping videos

Example: all AVI videos in `~/Videos` are endlessly looped:

```sh
FileGlobLivestream ~/Videos youtube -glob "*.avi" -loop
```

## stream m3u8 playlist

m3u8 playlist [example](./Examples/playlist_m3u8.py)

## stream all audio files in directory

Glob list of video files to stream. Suggest including a static -image (could be your logo):

```sh
FileGlobLivestream path site -glob glob_pattern -image image
```

* `path` path to where video files are
* `glob_pattern` e.g. `*.avi` pattern matching video files
* `-image` filename of image to use as stream background (REQUIRED for most websites)

Example: stream all .mp3 audio under `~/music` directory:

```sh
FileGlobLivestream ~/music youtube -glob "*.mp3" -image mylogo.jpg
```

Example: stream all .mp3 audio in `~/music` with an animated GIF or video clip repeating:

```sh
FileGlobLivestream ~/music youtube -glob "*.mp3" -image myclip.avi
```

or

```sh
FileGlobLivestream ~/music youtube -glob "*.mp3" -image animated.gif
```
