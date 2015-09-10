#!/usr/bin/env python
"""dreambox-pythonlib setup.py"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from setuptools import find_packages

setup(name='dreambox',
      version=__import__('dreambox').__version__,
      description='A general purpose library for dreambox ops team',
      author='Chengkai Liang',
      author_email='chengkai.liang@dreambox.com',
      url='https://bitbucket.org/chengkai/dreambox-pythonlib',
      install_requires=['funcy', 'awscli', 'docopt', 'pyyaml'],
      packages=find_packages(),
      classifiers=[
           "Programming Language :: Python",
           "Development Status :: 1 - alpha",
           "Environment :: Console",
           "Intended Audience :: Developers",
           "License :: OSI Approved :: Apache Software License",
           "Operating System :: OS Independent",
           'Topic :: System :: Systems Administration',
      ]
      )
