#!/usr/bin/env python
tests_require=['nose','coveralls']
from setuptools import setup,find_packages

setup(name='PyLivestream',
      packages=find_packages(),
      version = '1.1.0',
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scivision/PyLivestream',
      description='Easy streaming using FFmpeg to YouTube Live, Periscope, Facebook Live.',
      long_description=open("README.rst").read(),
      python_requires='>=3.6',
      tests_require=tests_require,
      extras_require={'tests':tests_require},
      classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: End Users/Desktop',
      'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
      'Operating System :: OS Independent',
      'Programming Language :: Python :: 3',
      'Topic :: Multimedia :: Graphics :: Capture :: Screen Capture',
      'Topic :: Multimedia :: Sound/Audio :: Capture/Recording',
      ],
	  )

