
import zmq
import time

context = zmq.Context.instance()
socket = context.socket(zmq.REQ)

socket.connect("tcp://localhost:8888")
# socket.connect("ipc://test")

# initalize variables, otherwise first time measurement is too long
# because variables are initalized there
counter = 0
time_sum = 0
time1 = 0.0
time2 = 0.0

while True:
    ret = ""
    # get timestamp 1
    time1 = time.time_ns()
    # send and receive a short message
    socket.send_string("!")
    # both functions are blocking
    ret = socket.recv_string()
    # get timestamp 2
    time2 = time.time_ns()

    # calculation of mean value
    counter += 1
    dt_us = (time2 - time1) / 1000.0
    time_sum += dt_us
    print("Times: ", time1, time2, dt_us)
    print(
        "ZMQ: sent: ! received: ",
        ret,
        " in ",
        dt_us,
        " µs, mean: ",
        time_sum /
        counter)
    time.sleep(0.5)
