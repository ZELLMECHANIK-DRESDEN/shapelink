"""Receive data in real-time from a Shape-In instance via zmq"""
import abc

import numpy as np
from PySide2 import QtCore
import zmq

from . import msg_def
from .util import qstream_read_array


class EventData:
    def __init__(self):
        self.id = -1
        self.scalars = list()
        self.traces = list()
        self.images = list()


class ShapeLinkPlugin(abc.ABC):
    def __init__(self, bind_to='tcp://*:6666', verbose=False):
        """Shape-Link plug-in meta class

        Parameters
        ----------
        bind_to: str
            IP and port to bind to (where Shape-In runs)
        verbose: bool
            Set to `True` to see additional debugging information.
        """
        super(ShapeLinkPlugin, self).__init__()
        self.verbose = verbose
        if self.verbose:
            print(" Init Shape-Link")
            print(" Bind to: ", bind_to)
        self.zmq_context = zmq.Context.instance()
        self.socket = self.zmq_context.socket(zmq.REP)
        self.socket.RCVTIMEO = 5000
        self.socket.SNDTIMEO = 5000
        self.socket.bind(bind_to)
        self.scalar_len = 0
        self.vector_len = 0
        self.image_len = 0
        self.registered_data_format = EventData()
        self.registered = False

    def after_register(self):
        """Called after registration with Shape-In is complete"""
        pass

    def after_transmission(self):
        """Called after Shape-In ends data transmission"""

    def handle_messages(self):
        """Handle messages from Shape-In

        Please don't override this function. Use
        :func:`ShapeLinkPlugin.handle_event` for your customized plugins.
        """
        # read first byte
        try:
            # get message from socket
            rcv = QtCore.QByteArray(self.socket.recv())
        except zmq.error.ZMQError:
            if self.verbose:
                print(" ZMQ Error - timed out")
            return
        rcv_stream = QtCore.QDataStream(rcv, QtCore.QIODevice.ReadOnly)
        r = rcv_stream.readInt64()

        send_data = QtCore.QByteArray()
        send_stream = QtCore.QDataStream(send_data, QtCore.QIODevice.WriteOnly)

        if r == msg_def.MSG_ID_REGISTER:
            # register
            self.registered_data_format.scalars = rcv_stream.readQStringList()
            self.registered_data_format.traces = rcv_stream.readQStringList()
            self.registered_data_format.images = rcv_stream.readQStringList()
            send_stream.writeInt64(msg_def.MSG_ID_REGISTER_ACK)
            if self.verbose:
                print(" Registered data container formats:")
                print("  scalars: ", self.registered_data_format.scalars)
                print("  traces:  ", self.registered_data_format.traces)
                print("  images:  ", self.registered_data_format.images)
            self.after_register()
        elif r == msg_def.MSG_ID_EOT:
            # EOT message
            send_stream.writeInt64(msg_def.MSG_ID_EOT_ACK)
            self.after_transmission()
        elif r >= 0:
            # data package with id r
            # check if id was received already
            # unpack data
            e = EventData()

            e.id = r

            e.scalars = qstream_read_array(rcv_stream, np.float64)
            assert len(e.scalars) == len(self.registered_data_format.scalars)

            n_traces = rcv_stream.readUInt32()
            assert n_traces == len(self.registered_data_format.traces)
            # read traces piece by piece
            for i in range(n_traces):
                e.traces.append(qstream_read_array(rcv_stream, np.int16))

            n_images = rcv_stream.readUInt32()
            assert n_images == len(self.registered_data_format.images)
            # read images piece by piece
            for i in range(n_images):
                e.images.append(qstream_read_array(rcv_stream, np.uint8))
                # and re-shape
                # ???
            # pass event object to user-defined method
            ret = self.handle_event(e)
            send_stream.writeBool(ret)
        else:
            # unknown message
            raise ValueError("Received unknown message header!")
        self.socket.send(send_data)

    @abc.abstractmethod
    def handle_event(self, event_data: EventData) -> bool:
        """Abstract method to be overridden by plugins implementations"""
        return False
