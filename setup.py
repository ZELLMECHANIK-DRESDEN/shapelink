#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import dirname, realpath, exists
from setuptools import setup
import sys


author = u"Paul Müller"
authors = ["Philipp Rosendahl", author]
name = 'shapelink'
description = 'Inter-process communication with Shape-In'
year = "2021"
long_description = """
Shape-Link is the endpoint for receiving the real-time
data stream from Shape-In (ZELLMECHANIK DRESDEN) and provides
the data to custom programs
"""

sys.path.insert(0, realpath(dirname(__file__)) + "/" + name)
from _version import version  # noqa: E402


setup(
    name=name,
    author=author,
    author_email='dev@craban.de',
    url='https://github.com/ZELLMECHANIK-DRESDEN/shapelink',
    version=version,
    packages=[name],
    package_dir={name: name},
    license="GPL v3",
    description=description,
    long_description=open('README.rst').read() if exists('README.rst') else '',
    install_requires=[
        "click>=7",
        "dclab>0.32.2",
        "numpy>=1.7.0",
        "PySide2",
        "pyzmq",
        ],
    entry_points={
        "console_scripts": [
            "shape-link = shapelink.cli:main",
        ],
    },
    setup_requires=['pytest-runner'],
    python_requires=">=3.6",
    tests_require=["pytest"],
    include_package_data=True,
    keywords=["fcs", "flow cytometry", "flow cytometry standard"],
    classifiers=['Operating System :: OS Independent',
                 'Programming Language :: Python :: 3',
                 'Topic :: Scientific/Engineering :: Visualization',
                 'Intended Audience :: Science/Research',
                 ],
    platforms=['ALL'],
    )
