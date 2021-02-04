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
    def __init__(self, destination="tcp://localhost:6666", verbose=False):
        self.verbose = verbose
        if self.verbose:
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
        """Register parameters that are sent to other processes"""
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
            if self.verbose:
                print("Send registration message")
            # send the message over the socket
            self.socket.send(msg)
            # get ACK before return
            rcv = QtCore.QByteArray(self.socket.recv())
        except zmq.error.ZMQError:
            if self.verbose:
                print("ZMQ Error")
            return

        rcv_stream = QtCore.QDataStream(rcv, QtCore.QIODevice.ReadOnly)
        r = rcv_stream.readInt64()
        if r == msg_def.MSG_ID_REGISTER_ACK:
            if self.verbose:
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
        """Send a single event to the other process"""

        # prepare message in byte stream
        msg = QtCore.QByteArray()
        msg_stream = QtCore.QDataStream(msg, QtCore.QIODevice.WriteOnly)
        msg_stream.writeInt64(event_id)

        assert len(scalar_values) == self.scalar_len
        assert len(vector_values) == self.vector_len
        assert len(image_values) == self.image_len

        assert np.issubdtype(scalar_values.dtype, np.floating)

        qstream_write_array(msg_stream, scalar_values)
        msg_stream.writeUInt32(self.vector_len)
        for e in vector_values:
            assert e.dtype == np.int16, "fluorescence data is int16"
            qstream_write_array(msg_stream, e)

        msg_stream.writeUInt32(self.image_len)
        for e in image_values:
            assert e.dtype == np.uint8, "image data is uint8"
            qstream_write_array(msg_stream, e.flatten())

        try:
            # send the message over the socket
            self.socket.send(msg)
            # get ACK before return
            rcv_data = QtCore.QByteArray(self.socket.recv())
        except zmq.error.ZMQError:
            if self.verbose:
                print("ZMQ Error")
            return
        rcv_stream = QtCore.QDataStream(rcv_data, QtCore.QIODevice.ReadOnly)
        self.respones.append(rcv_stream.readBool())
        return self.respones[-1]

    def send_end_of_transmission(self):
        """Send end of transmission packet"""
        # prepare message in byte stream
        msg = QtCore.QByteArray()
        msg_stream = QtCore.QDataStream(msg, QtCore.QIODevice.WriteOnly)
        msg_stream.writeInt64(msg_def.MSG_ID_EOT)

        # reset state
        self.registered = False

        # print responses
        if self.verbose:
            print(self.respones)
        try:
            if self.verbose:
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
            if self.verbose:
                print("EOT success")


def start_simulator(path, features=None, verbose=1):
    """Run a Shape-In simulator using data from an RT-DC dataset"""
    with dclab.new_dataset(path) as ds:
        if verbose:
            print("Opened dataset", ds.identifier, ds.title)
        if features is None:
            features = ds.features_innate
        s = ShapeInSimulator()
        im_features = sorted({"image", "mask"}
                             & set(ds.features)
                             & set(features))
        sc_features = sorted(set(ds.features_scalar)
                             & set(ds.features)
                             & set(features))
        if "trace" in ds and "trace" in features:
            tr_features = sorted(ds['trace'].keys())
        else:
            tr_features = []

        s.register_parameters(
            scalar_hdf5_names=sc_features,
            vector_hdf5_names=tr_features,
            image_hdf5_names=im_features,
            settings_names=[],
            settings_values=[],
        )

        t0 = time.perf_counter_ns()
        c = 0

        if verbose:
            print("Send event data:")
        for event_index in range(len(ds)):
            scalars = list()
            vectors = list()
            images = list()
            for feat in sc_features:
                scalars.append(ds[feat][event_index])
            for feat in tr_features:
                tr = np.array(ds['trace'][feat][event_index], dtype=np.int16)
                vectors.append(tr)
            for feat in im_features:
                im = np.array(ds[feat][event_index], dtype=np.uint8)
                images.append(im)

            s.send_event(event_index,
                         np.array(scalars, dtype=np.float64),
                         vectors,
                         images)
            c += 1

        t1 = time.perf_counter_ns()

        # Finally stop with EOT message
        s.send_end_of_transmission()

        dt = (t1 - t0) * 1e-9

        if verbose:
            print("Simulation event rate: {:.5g} Hz".format(c / dt))
            print("Simulation time: {:.5g} s".format(dt))
