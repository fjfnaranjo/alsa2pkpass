#!/usr/bin/env python

from distutils.core import setup

setup(
    name="alsa2pkpass",
    entry_points={
        'console_scripts': ['alsa2pkpass=alsa2pkpass:main'],
    },
    install_requires=['PyPDF2==1.26.0'],
)

