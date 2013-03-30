from datetime import datetime
from multiprocessing import Process

__author__ = 'guglielmo'

import time
import zmq
import pprint
from faker import Factory


SERVER_HOST = '192.168.1.127'
MAILBIN_QUEUE_ADDR = "tcp://%s:5558" % SERVER_HOST


def form_handler():
    """
    Simulate the main form request handler.
    Send a fake message to the mailbin queue
    """
    context = zmq.Context()

    # socket to sending messages to save
    save_sender = context.socket(zmq.PUSH)

    try:
        save_sender.connect(MAILBIN_QUEUE_ADDR)
    except Exception, e:
        print "Error connecting: %s" % e

    while (True):
        # simulate mail form content
        faker = Factory.create()

        data = {
            'first_name': faker.firstName(),
            'last_name': faker.lastName(),
            'email': faker.email(),
            'created_at': faker.dateTimeThisMonth().strftime('%Y%m%d'),
            'ip': faker.ipv4(),
            'user_agent': faker.userAgent(),
            'service_uri': 'http://www.voisietequi.it/'
        }

        # send message to sender
        save_sender.send_json(data)
        pprint.pprint(data)

        # take it easy
        time.sleep(0.5)


if __name__ == "__main__":
    Process(target=form_handler).start()
