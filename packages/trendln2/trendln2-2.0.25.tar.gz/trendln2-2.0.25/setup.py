#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Support and Resistance Trendlines Calculator for Financial Analysis
# https://pypi.org/project/trendln
# https://github.com/GregoryMorse/trendln

"""Support and Resistance Trendlines Calculator for Financial Analysis"""

# pip install twine

# cd /D D:\OneDrive\Documents\Projects\trader\trendln
# del dist\*.tar.gz
# "%ProgramFiles%\Python37\python.exe" setup.py sdist
# "%ProgramFiles%\Python37\scripts\twine.exe" upload dist/* --verbose
# "%ProgramFiles%\Python37\scripts\pip.exe" install trendln --upgrade
# "%ProgramData%\Anaconda3\scripts\pip.exe" install trendln --upgrade
# import importlib
# importlib.reload(trendln)

import io
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with io.open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='trendln2',
    version="2.0.25",
    description='Support and Resistance Trend lines Calculator for Financial Analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ShriekinNinja/trendln',
    author='Gregory Morse',
    author_email='gregory.morse@live.com',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',

        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Office/Business :: Financial',
        'Topic :: Office/Business :: Financial :: Investment',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'Programming Language :: Python :: 3.13',
    ],
    platforms=['any'],
    keywords='trendlines, trend lines, trend, support, resistance, trends, technical, indicators, financial, analysis',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'examples']),
    install_requires=['numpy>=2.3.5', 'findiff>=0.12.1', 'scikit-image>=0.25.2',
                      'pandas>=2.3.3', 'matplotlib>=3.10.7'],
)
