#!/usr/bin/env python
install_requires=[]
tests_require=['pytest','nose','coveralls']
from setuptools import setup,find_packages

setup(name='PyLivestream',
      packages=find_packages(),
      version = '1.6.2',
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scivision/PyLivestream',
      description='Easy streaming using FFmpeg to YouTube Live, Periscope, Facebook Live, Twitch, ...',
      long_description=open("README.rst").read(),
      python_requires='>=3.5',
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'tests':tests_require},
      classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Environment :: Console',
      'Intended Audience :: End Users/Desktop',
      'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
      'Operating System :: OS Independent',
      'Programming Language :: Python :: 3.5',
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3.7',
      'Topic :: Multimedia :: Graphics :: Capture :: Screen Capture',
      'Topic :: Multimedia :: Sound/Audio :: Capture/Recording',
      'Topic :: Multimedia :: Video :: Capture',
      ],
      scripts=['FileGlobLivestream.py','ScreenshareLivestream.py',
               'FileLoopLivestream.py','ScreenCapture2disk.py','WebcamLivestream.py'],
      include_package_data=True,
    )

