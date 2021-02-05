"""Utility functions

These functions replicate QDataStreams behavior in C++.
In PySide2 QDataStream does not accept array type data.

In C++ an array is serialized by writing:
1) Uint32 number of elements
2) type array elements

more significant bytes are written first. (big-endian)

if numpy "to_bytes" is used the native little-endian
format appears
"""
import numpy as np
from PySide2 import QtCore


def qstream_write_array(stream: QtCore.QDataStream, array: np.array) -> int:
    """
    Write array data to a stream with a specified type
    :param stream:
    :param array:
    :return:
    """
    data_array = QtCore.QByteArray(array.tobytes())
    stream << data_array
    return len(array)


def qstream_read_array(stream: QtCore.QDataStream,
                       datatype: np.dtype) -> np.array:
    """Read array data from a stream with a specified type"""
    data_array = QtCore.QByteArray()
    stream >> data_array
    data = np.frombuffer(data_array, dtype=datatype)
    return data


if __name__ == '__main__':
    # prepare message in byte stream
    msg = QtCore.QByteArray()
    msg_stream = QtCore.QDataStream(msg, QtCore.QIODevice.ReadWrite)

    qstream_write_array(msg_stream, np.array(
        [1, 2, 3, 5.23, 6], dtype=np.int16))
    qstream_write_array(msg_stream, np.array(
        [1.1, 3, 4.234, .2342, 42.23, 234.34, 23.33, .22], dtype=np.float64))
    qstream_write_array(msg_stream, np.array(
        [3, 4, 5, 6, 255, 0, 0, 0, 0, 0, 5, 98], dtype=np.uint8))

    print("After write")
    print(msg)

    print("Recover message")
    msg_stream.device().reset()

    print(qstream_read_array(msg_stream, np.int16))
    print(qstream_read_array(msg_stream, np.float64))
    print(qstream_read_array(msg_stream, np.uint8))
