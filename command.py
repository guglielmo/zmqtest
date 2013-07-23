__author__ = 'guglielmo'

import zmq
import time
import json
from multiprocessing import Process


def send_command(pub_socket):
    topic = 'politiche2013'
    messagedata = json.dumps({ 'cmd': 'configure', 'response_channel': "tcp://localhost:5557"})
    print "%s %s" % (topic, messagedata)
    pub_socket.send("%s %s" % (topic, messagedata))
    pub_socket.close()


def cmd_reply_handler():
    print "Listening to response from configured computers"

    context = zmq.Context()

    results_receiver = context.socket(zmq.PULL)
    results_receiver.bind("tcp://*:5557")
    results_receiver.RCVTIMEO = 1000 #sets timeout

    poller = zmq.Poller()
    poller.register(results_receiver, zmq.POLLIN)

    should_continue = True
    while should_continue:
        # check if there are any results to receive
        socks = dict(poller.poll(200))
        if results_receiver in socks and socks[results_receiver] == zmq.POLLIN:
            message = results_receiver.recv()
            print "Computer responded: %s" % message
            print "Will continue"
        else:
            should_continue = False
            print "Will stop"

if __name__ == "__main__":

    #
    # setup sockets and connections
    #
    context = zmq.Context()

    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind("tcp://*:5556")


    #
    # wait for connections (handshake, ...)
    #
    time.sleep(0.2)

    #
    # send command and listens for replies
    send_command(pub_socket)

    p = Process(target=cmd_reply_handler)
    p.start()
    p.join()



