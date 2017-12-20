#!/usr/bin/env python
tests_require=['nose','coveralls']
from setuptools import setup,find_packages

setup(name='YouTubeLiveFFmpeg',
      packages=find_packages(),
      version = '1.0.2',
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scivision/ffmpeg-youtube-live',
      description='Easy streaming using FFmpeg to YouTube Live.',
      long_description=open("README.rst").read(),
      python_requires='>=3.6',
      tests_require=tests_require,
      extras_require={'tests':tests_require},
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

