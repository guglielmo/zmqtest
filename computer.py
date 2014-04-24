from multiprocessing import Process
import time

__author__ = 'guglielmo'

import random
import zmq


SERVER_HOST = 'localhost'
CMD_SUB_QUEUE_ADDR  = "tcp://%s:5556" % SERVER_HOST
REPLY_PUSH_QUEUE_ADDR = "tcp://%s:5557" % SERVER_HOST
SAVE_PUSH_QUEUE_ADDR = "tcp://%s:5558" % SERVER_HOST

def main_task_handler():
    """
    Simulate the main task. Do something (compute a result),
    and send a message to the saver
    """
    context = zmq.Context()

    # socket to sending messages to save
    save_sender = context.socket(zmq.PUSH)
    save_sender.connect(SAVE_PUSH_QUEUE_ADDR)

    c = 0
    while (True):
        # simulate some very complex computation
        (x, y) = (random.gauss(0, 1), random.gauss(0, 1))
        result = { 'unit': computer_id, 'counter': c, 'x' : x, 'y': y}

        # send message to sender
        save_sender.send_json(result)

        # take it easy
        time.sleep(1)

        c += 1

def cmd_handler():
    """
    Simulate listening to a cmd sent by the master, and replying to it
    """
    context = zmq.Context()

    # socket to receive commands (a subscription to ELECTION_CODE channel)
    cmd_socket = context.socket(zmq.SUB)
    cmd_socket.connect ("tcp://%s:5556" % SERVER_HOST)
    topicfilter = "politiche2013"
    cmd_socket.setsockopt(zmq.SUBSCRIBE, topicfilter)

    # socket to send replies
    reply_sender = context.socket(zmq.PUSH)
    reply_sender.connect("tcp://%s:5557" % SERVER_HOST)

    # main loop
    while True:
        print "Aye sir, unit {0} ready for your commands ...".format(computer_id)
        # wait for a command
        string = cmd_socket.recv()

        # action
        print "Message received: '%s'" % (string,)

        # send reply to server
        print "Sending reply to server"
        reply = { 'unit' : computer_id, 'status' : 'configured'}
        reply_sender.send_json(reply)


if __name__ == "__main__":
    computer_id = random.randrange(1,10000)
    Process(target=cmd_handler).start()
    Process(target=main_task_handler).start()
