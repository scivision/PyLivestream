#!/usr/bin/env python
from setuptools import setup

setup(name='YouTubeLiveFFmpeg',
      packages=['youtubelive_ffmpeg'],
      version = '0.2.0',
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scivision/ffmpeg-youtube-live',
      description='Easy streaming using FFmpeg to YouTube Live.',
      long_description=open("README.rst").read(),
      python_requires='>=3.6',
      classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: End Users/Desktop',
      'License :: OSI Approved :: MIT License',
      'Operating System :: OS Independent',
      'Programming Language :: Python :: 3',
      'Topic :: Multimedia :: Graphics :: Capture :: Screen Capture',
      'Topic :: Multimedia :: Sound/Audio :: Capture/Recording',
      ],
	  )

