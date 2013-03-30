__author__ = 'guglielmo'

import zmq
import random
import sys
import time

port = "5556"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s" % port)

while True:
    zipcode = random.randrange(10000,10002)
    messagedata = random.randrange(1,215) - 80
    print "%d %d" % (zipcode, messagedata)
    socket.send("%d %d" % (zipcode, messagedata))
    time.sleep(1)