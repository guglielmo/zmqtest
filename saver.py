__author__ = 'guglielmo'

import zmq
from multiprocessing import Process


def req_handler():
    context = zmq.Context()
    req_receiver = context.socket(zmq.PULL)
    req_receiver.bind("tcp://*:5558")

    poller = zmq.Poller()
    poller.register(req_receiver, zmq.POLLIN)

    print "Listening to save requests from computers"
    while True:
        socks = dict(poller.poll())
        if req_receiver in socks and socks[req_receiver] == zmq.POLLIN:
            message = req_receiver.recv()
            print "Computer requested a save: %s" % message


if __name__ == "__main__":
    p = Process(target=req_handler)
    p.start()
    p.join()
