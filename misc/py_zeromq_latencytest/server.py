import zmq

context = zmq.Context.instance()
socket = context.socket(zmq.REP)

socket.bind("tcp://*:8888")
# socket.bind("ipc://test")


while True:
    r = socket.recv_string()
    socket.send_string("&")
