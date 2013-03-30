This directory contains some source code examples of how to work with zmq.

* `Request - Response`_
* `Publish and Subscribe`_
* `Voisietequi prototype`_
* `Fake mail form`_


.. _`Request - Response`:

Request - Response example
--------------------------

::

          #------------#
          |   Client   |
          +------------+
          |    REQ     |
          '---+--------'
              |    ^
              |    |
        Hello |    | World
              |    |
              v    |
          .--------+---.
          |    REP     |
          +------------+
          |   Server   |
          #------------#


reqrep_server.py
  Listens on a ``zmq.REP`` socket on port 5556.
  Whenever a message is received, after 1 sec, sends a reply, over the same socket::

        message = socket.recv()
        time.sleep (1)
        socket.send("World from %s" % port)

reqrep_client.py
  The client connects to a ``zmq.REQ`` socket on port 5556. It loops 10 times, sending a request and
  waiting for a response::

    socket.send ("Hello")
    message = socket.recv()



.. _`Publish and Subscribe`:

Publish - Subscribe example
---------------------------

::

                   #-------------#
                   |  Publisher  |
                   +-------------+
                   |     PUB     |
                   '-------------'
                        bind
                          |
                          |
                       updates
                          |
          .---------------+---------------.
          |               |               |
       updates         updates         updates
          |               |               |
          |               |               |
          v               v               v
       connect         connect         connect
    .------------.  .------------.  .------------.
    |    SUB     |  |    SUB     |  |    SUB     |
    +------------+  +------------+  +------------+
    | Subscriber |  | Subscriber |  | Subscriber |
    #------------#  #------------#  #------------#


pub_server.py
  Listens on a ``zmq.PUB`` socket on port 5556.
  Continuously spits out random temperature data relative to 3 different zipcodes (topics)::

    zipcode = random.randrange(10000,10002)
    messagedata = random.randrange(1,215) - 80
    socket.send("%d %d" % (zipcode, messagedata))

sub_client.py
  Connects to a ``zmq.SUB`` socket on port 5556. Sets a subscription to one of the three zipcodes (topic).
  After receiving 5 messages, computes the average::

    socket.setsockopt(zmq.SUBSCRIBE, "10001")
    total_value = 0
    for update_nbr in range (5):
        string = socket.recv()
        topic, messagedata = string.split()
        total_value += int(messagedata)
        print topic, messagedata


.. _`Voisietequi prototype`:

Complex Voisietequi prototype
-----------------------------

In Voisietequi there is a **server** which distributes
computation requests over different **computers**. Details can be found on voisietequi
github repository.

Computers must be *discovered* and *configured*, by the central server, so that there is no
need to specify configuration settings when launching them.

Computers should also send the results of their computation back to the server, in order to save
the results in a database, for example.


Configuration and discovery
===========================

::

                   #-------------#
                   |    Server   |
                   +-------------+
                   |     PUB     |
                   '-------------'
                      bind:5556
                          |
                          |
                       commands
                          |
          .---------------+---------------.
          |               |               |
       commands        commands        commands
          |               |               |
          |               |               |
          v               v               v
     connect:5556    connect:5556    connect:5556
    .------------.  .------------.  .------------.
    |    SUB     |  |    SUB     |  |    SUB     |
    +------------+  +------------+  +------------+
    |  Computer  |  |  Computer  |  |  Computer  |
    +------------+  +------------+  +------------+
    |    PUSH    |  |    PUSH    |  |    PUSH    |
    '-----+------'  '-----+------'  '-----+------'
     connect:5557    connect:5557    connect:5557
          |               |               |
          '---------------+---------------'
                          |
                       results
                          |
                          v
                      bind:5557
                   .-------------.
                   |    PULL     |
                   +-------------+
                   |   Server    |
                   #-------------#


command.py
  emulates the vsq-server, there are 2 connections in the same process:

    * binds to ``zmq.PUB`` socket pn port 5556, to send command to all parties interested
    * binds to ``zmq.PULL`` socket on port 5557, to receive all command response results

  a ``configure`` command is sent and the reply message is listened to; listening is done
  through a poller_ in the ``cmd_reply_handler`` function; once the reply message is found in the poll,
  it is consumed and connections are closed::

      should_continue = True
      while should_continue:
        socks = dict(poller.poll(200))
        if results_receiver in socks and socks[results_receiver] == zmq.POLLIN:
            message = results_receiver.recv()
            print "Computer responded: %s" % message
        else:
            should_continue = False


computer.py
  emulates the vsq-computer; it has 2 parallel tasks, running:

    * ``main_task_handler``: simulates the computation task
      sends results of the computation to the **saver**, see next section
    * ``cmd_handler``: handle configuration commands sent by server: connect to a ``zmq.SUB`` socket on port 5556
      and continuously awaits for commands there, once received, a reply is immediatly sent back through
      a connection to a ``zmq.PUSH`` on port 5557


.. _poller: https://learning-0mq-with-pyzmq.readthedocs.org/en/latest/pyzmq/multisocket/zmqpoller.html



Saving the results
==================

::

    #------------#  #------------#  #------------#
    |  Computer  |  |  Computer  |  |  Computer  |
    +------------+  +------------+  +------------+
    |    PUSH    |  |    PUSH    |  |    PUSH    |
    '-----+------'  '-----+------'  '-----+------'
     connect:5558    connect:5558    connect:5558
          |               |               |
          '---------------+---------------'
                          |
                       results
                          |
                          v
                       bind:5558
                   .-------------.
                   |    PULL     |
                   +-------------+
                   |    Server   |
                   #-------------#


computer.py
  emulates the vsq-computer; it has 2 parallel tasks, running:

    * ``main_task_handler``: simulates the computation task
      sends results of the computation to the **saver**, connecting to a ``zmq.PUSH`` on port 5558::

          save_sender.send_json(result)

    * ``cmd_handler``: handle configuration commands sent by server: see previous section

saver.py
   binds to ``zmq.PULL`` socket on port 5558, to receive all computation results;
   results are checked through a **poller**::

       while True:
        socks = dict(poller.poll())
        if req_receiver in socks and socks[req_receiver] == zmq.POLLIN:
            message = req_receiver.recv()
            print "Computer requested a save: %s" % message



.. _`Fake mail form`:

Fake mail form (mailbin)
------------------------

::

    #--------------#  #--------------#  #--------------#
    |  FakerScript |  |  FakerScript |  |  FakerScript |
    +--------------+  +--------------+  +--------------+
    |     PUSH     |  |     PUSH     |  |     PUSH     |
    '------+-------'  '------+-------'  '------+-------'
      connect:5558      connect:5558      connect:5558
           |                 |                 |
           '-----------------+-----------------'
                             |
                           data
                             |
                             v
                          bind:5558
                      .-------------.
                      |    PULL     |
                      +-------------+
                      |   Mailbin   |
                      #-------------#

Pushes fake mail form post data to the ``mailbin`` service.
The form data are pushed to a ``zmq.PUSH`` socket on port 5558, and it is received
at the *Mailbin* service (``zmq.PULL`` socket with a **poller**).
