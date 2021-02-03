"""Shape-Link: Inter-process communication with Shape-In

This library is the endpoint for receiving the real-time
data stream from Shape-In (ZELLMECHANIK DRESDEN) and provides
the data to custom programs
"""
import zmq
import dclab

from .endpoint import Endpoint
from .shapein_simulator import Shapein_simulator
