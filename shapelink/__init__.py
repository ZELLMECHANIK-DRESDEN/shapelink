"""Shape-Link: Inter-process communication with Shape-In

This library is the endpoint for receiving the real-time
data stream from Shape-In (ZELLMECHANIK DRESDEN) and provides
the data to custom programs
"""
# flake8: noqa: F401
from .shapelink_plugin import ShapeLinkPlugin
from ._version import version as __version__
