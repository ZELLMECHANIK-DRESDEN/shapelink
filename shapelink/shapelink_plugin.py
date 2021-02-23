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
        self.image_shape = None
        self.image_shape_len = 2
        self.hdf5_names = EventData()
        self.registered = False

    def after_features_request(self):
        """Called after the request for features"""
        pass

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

        if r == msg_def.MSG_ID_FEATURE_REQ:
            # Allow plugin to request features
            feats = self.run_features_request_message(send_stream)
            send_stream.writeQStringList(feats)
            self.after_features_request()

        elif r == msg_def.MSG_ID_REGISTER:
            # register
            self.run_register_message(rcv_stream, send_stream)
            self.after_register()

        elif r == msg_def.MSG_ID_EOT:
            # End of Transmission (EOT) message
            self.run_EOT_message(send_stream)
            self.after_transmission()

        elif r >= 0:
            e = self.run_event_message(r, rcv_stream)
            # pass event object to user-defined method
            ret = self.handle_event(e)
            send_stream.writeBool(ret)

        else:
            # unknown message
            raise ValueError("Received unknown message header: {}".format(r))
        self.socket.send(send_data)

    def run_features_request_message(self, send_stream):
        """Called before registration. The user can specify features for
        Shape-In to send. This limits the data being transferred.
        This can be useful for plugins that require only specific features.

        feats is a list of three lists. The lists are sc, tr, and im
        """

        # user chooses what features they want in their plugin using:
        feats = self.choose_features()
        return feats

    def run_register_message(self, rcv_stream, send_stream):
        # register
        self.hdf5_names.scalars = rcv_stream.readQStringList()
        self.hdf5_names.traces = rcv_stream.readQStringList()
        self.hdf5_names.images = rcv_stream.readQStringList()
        self.image_shape = qstream_read_array(rcv_stream, np.uint16)

        self.scalar_len = len(self.hdf5_names.scalars)
        self.vector_len = len(self.hdf5_names.traces)
        self.image_len = len(self.hdf5_names.images)
        assert self.image_shape_len == len(self.image_shape)

        send_stream.writeInt64(msg_def.MSG_ID_REGISTER_ACK)
        if self.verbose:
            print(" Registered data container formats:")
            print("  scalars: ", self.hdf5_names.scalars)
            print("  traces:  ", self.hdf5_names.traces)
            print("  images:  ", self.hdf5_names.images)
            print("  image_shape:  ", self.image_shape)

    def run_event_message(self, r, rcv_stream):
        # data package with id r
        # check if id was received already
        # unpack data
        e = EventData()

        e.id = r

        e.scalars = qstream_read_array(rcv_stream, np.float64)
        assert len(e.scalars) == self.scalar_len

        n_traces = rcv_stream.readUInt32()
        assert n_traces == self.vector_len
        # read traces piece by piece
        for i in range(n_traces):
            e.traces.append(qstream_read_array(rcv_stream, np.int16))

        n_images = rcv_stream.readUInt32()
        assert n_images == self.image_len
        # read images piece by piece, checking for binary mask
        for im_name in self.hdf5_names.images:
            if im_name == "mask":
                e.images.append(qstream_read_array(rcv_stream, np.bool_))
            else:
                e.images.append(qstream_read_array(rcv_stream, np.uint8))
            for i, im in enumerate(e.images):
                e.images[i] = np.reshape(e.images[i], self.image_shape)
        return e

    def run_EOT_message(self, send_stream):
        # End of Transmission (EOT) message
        send_stream.writeInt64(msg_def.MSG_ID_EOT_ACK)

    @abc.abstractmethod
    def handle_event(self, event_data: EventData) -> bool:
        """Abstract method to be overridden by plugins implementations"""
        return False

    @abc.abstractmethod
    def choose_features(self):
        """Abstract method to be overridden by plugins implementations"""
        return list()
