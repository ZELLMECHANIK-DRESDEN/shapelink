
import zmq
from shapelink.shapein_simulator import ShapeInSimulator, start_simulator


def test_ShapeInSimulator_zmq_attributes(ShapeInSimulator=ShapeInSimulator):
    ''' Check the ZMQ aspects of the simulator,
    then close the context and sockets. '''
    s = ShapeInSimulator()
    assert isinstance(s.zmq_context, zmq.Context)
    assert isinstance(s.socket, zmq.Socket)
    # close the context
    s.zmq_context.destroy()
    assert s.zmq_context.closed == True, "Should be True"
    assert s.socket.closed == True, "Should be True"


def test_ShapeInSimulator_destination(ShapeInSimulator=ShapeInSimulator):
    ''' Check the ZMQ aspects of the simulator,
    then close the context and sockets. '''
    s = ShapeInSimulator(destination="tcp://localhost:6667")
    assert s.destination == "tcp://localhost:6667"
    s.zmq_context.destroy()
