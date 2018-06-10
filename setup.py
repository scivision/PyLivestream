#!/usr/bin/env python
from typing import List
from setuptools import setup, find_packages

install_requires: List[str] = []
tests_require: List[str] = ['pytest', 'nose', 'coveralls', 'flake8', 'mypy']


setup(name='PyLivestream',
      packages=find_packages(),
      version='1.7.0',
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scivision/PyLivestream',
      description=('Easy streaming using FFmpeg to '
                   'YouTube Live, Periscope, Facebook Live, Twitch, ...'),
      long_description=open("README.md").read(),
      long_description_content_type="text/markdown",
      python_requires='>=3.6',
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'tests': tests_require, 'captions': 'tinytag'},
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Multimedia :: Graphics :: Capture :: Screen Capture',
          'Topic :: Multimedia :: Sound/Audio :: Capture/Recording',
          'Topic :: Multimedia :: Video :: Capture',
      ],
      scripts=['FileGlobLivestream.py', 'ScreenshareLivestream.py',
               'FileLoopLivestream.py', 'ScreenCapture2disk.py',
               'WebcamLivestream.py', 'MicrophoneLivestream.py',
               'visual_tests.py'],
      include_package_data=True,
      )
