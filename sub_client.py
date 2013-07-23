__author__ = 'guglielmo'

import sys
import zmq

port = "5556"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)

topicfilter = "10001"

print "Collecting updates from weather server at {0} ...".format(topicfilter)
socket.connect ("tcp://localhost:%s" % port)

# Subscribe to zipcode, default is NYC, 10001
socket.setsockopt(zmq.SUBSCRIBE, topicfilter)

# Process 5 updates
total_value = 0
update_nbr = 5
for t in range (update_nbr):
    string = socket.recv()
    topic, messagedata = string.split()
    total_value += int(messagedata)
    print topic, messagedata

print "Average temperature value for '%s' was %dC" % (topicfilter, total_value / update_nbr)
