"""Simulate a Shape-In instance

The communication is based on a simple REQ REP pattern
all methods return when the transmission was acknowledged
by the peer.
"""
import time
from typing import List

import dclab
import numpy as np
from PySide2 import QtCore
import zmq

from . import msg_def
from .util import qstream_write_array


class ShapeInSimulator:
    def __init__(self, destination="tcp://localhost:6666"):
        print("Init ShapeIn Simulator")
        print("Connect to: ", destination)
        self.zmq_context = zmq.Context.instance()
        self.socket = self.zmq_context.socket(zmq.REQ)
        self.socket.RCVTIMEO = 5000
        self.socket.SNDTIMEO = 5000
        self.socket.connect(destination)
        self.scalar_len = 0
        self.vector_len = 0
        self.image_len = 0
        self.registered = False
        self.respones = list()

    def register_parameters(self,
                            scalar_hdf5_names=None,
                            vector_hdf5_names=None,
                            image_hdf5_names=None,
                            settings_names=None,
                            settings_values=None
                            ):
        """
        Register which parameters are acquired and shall be
        send to the other process.

        :param scalar_hdf5_names:
        :param vector_hdf5_names:
        :param image_hdf5_names:
        :param settings_names:
        :param settings_values:
        :return:
        """
        if settings_values is None:
            settings_values = []
        if settings_names is None:
            settings_names = []
        if image_hdf5_names is None:
            image_hdf5_names = []
        if vector_hdf5_names is None:
            vector_hdf5_names = []
        if scalar_hdf5_names is None:
            scalar_hdf5_names = []
        assert len(settings_values) == len(
            settings_names), "Mismatch setting names and values"

        self.scalar_len = len(scalar_hdf5_names)
        self.vector_len = len(vector_hdf5_names)
        self.image_len = len(image_hdf5_names)
        self.respones.clear()

        # prepare message in byte stream
        msg = QtCore.QByteArray()
        msg_stream = QtCore.QDataStream(msg, QtCore.QIODevice.WriteOnly)
        msg_stream.writeInt64(msg_def.MSG_ID_REGISTER)

        # send parameters
        msg_stream.writeQStringList(scalar_hdf5_names)
        msg_stream.writeQStringList(vector_hdf5_names)
        msg_stream.writeQStringList(image_hdf5_names)

        # send settings
        for name, value in zip(settings_names, settings_values):
            msg_stream.writeQString(name)
            msg_stream.writeQVariant(value)

        try:
            print("Send registration message")
            # send the message over the socket
            self.socket.send(msg)
            # get ACK before return
            rcv = QtCore.QByteArray(self.socket.recv())
        except zmq.error.ZMQError:
            print("ZMQ Error")
            return

        rcv_stream = QtCore.QDataStream(rcv, QtCore.QIODevice.ReadOnly)
        r = rcv_stream.readInt64()
        if r == msg_def.MSG_ID_REGISTER_ACK:
            print("Registration ACK")
            self.registered = True
        else:
            print("Registering parameters failed!")
            self.registered = False

    def send_event(self,
                   event_id: int,
                   scalar_values: np.array,
                   # vector of vector of short
                   vector_values: List[np.array],
                   image_values: List[np.array]) -> bool:
        """
        Send a single event to the other process.

        :param event_id:
        :param scalar_values:
        :param vector_values:
        :param image_values:
        :return:
        """

        # prepare message in byte stream
        msg = QtCore.QByteArray()
        msg_stream = QtCore.QDataStream(msg, QtCore.QIODevice.WriteOnly)
        msg_stream.writeInt64(event_id)

        assert len(scalar_values) == self.scalar_len
        assert len(vector_values) == self.vector_len
        assert len(image_values) == self.image_len

        assert scalar_values.dtype == float

        qstream_write_array(msg_stream, scalar_values)
        # use this instead of the following
        # msg_stream.writeUInt32(self.scalar_len)
        # for e in scalar_values:
        #    msg_stream.writeFloat(e)

        msg_stream.writeUInt32(self.vector_len)
        for e in vector_values:
            assert e.dtype == np.int16
            qstream_write_array(msg_stream, e)

        msg_stream.writeUInt32(self.image_len)
        for e in image_values:
            assert e.dtype == np.uint8
            qstream_write_array(msg_stream, e.flatten())

        try:
            # send the message over the socket
            self.socket.send(msg)
            # get ACK before return
            rcv_data = QtCore.QByteArray(self.socket.recv())
        except zmq.error.ZMQError:
            print("ZMQ Error")
            return
        rcv_stream = QtCore.QDataStream(rcv_data, QtCore.QIODevice.ReadOnly)
        self.respones.append(rcv_stream.readBool())
        return self.respones[-1]

    def send_end_of_transmission(self):
        """
        Send end of transmission packet.
        :return:
        """
        # prepare message in byte stream
        msg = QtCore.QByteArray()
        msg_stream = QtCore.QDataStream(msg, QtCore.QIODevice.WriteOnly)
        msg_stream.writeInt64(msg_def.MSG_ID_EOT)

        # reset state
        self.registered = False

        # print responses
        print(self.respones)
        try:
            print("Sending EOT:", msg)
            # send the message over the socket
            self.socket.send(msg)
            # get ACK before return
            rcv_data = QtCore.QByteArray(self.socket.recv())
        except zmq.error.ZMQError:
            print("ZMQ Error - No ACK for EOT")
            return
        rcv_stream = QtCore.QDataStream(rcv_data, QtCore.QIODevice.ReadOnly)
        r = rcv_stream.readInt64()
        if r != msg_def.MSG_ID_EOT_ACK:
            print("Did not receive ACK for EOT but: ", r)
        else:
            print("EOT success")


def run(path):
    # Read a dataset from dcor via dclab
    with dclab.new_dataset(path) as ds:
        print("Opened dataset", ds.identifier, ds.title)
        s = ShapeInSimulator()
        img_features = list()
        if ('image' in ds.features):
            img_features.append('image')
        if ('mask' in ds.features):
            img_features.append('mask')
        s.register_parameters(ds.features_scalar,
                              ds['trace'].keys(),
                              img_features,
                              [], [])
        # for event_index in [55,33,22,11]:

        t0 = time.time_ns()
        c = 0

        print("Send event data:")
        for event_index in range(min(100, len(ds))):
            scalars = list()
            vectors = list()
            images = list()
            for e in ds.features_scalar:
                scalars.append(ds[e][event_index])
            for e in ds['trace'].keys():
                t = np.array(ds['trace'][e][event_index], dtype=np.int16)
                vectors.append(t)
            for e in img_features:
                i = np.array(ds[e][event_index], dtype=np.uint8)
                images.append(i)
            s.send_event(event_index, np.array(scalars), vectors, images)
            c += 1

        t1 = time.time_ns()

        # Finally stop with EOT message
        s.send_end_of_transmission()

        dt = (t1 - t0) / 1000000000.0

        print("Total time: ", dt)
        print("Events/s:   ", c / dt)
