from __future__ import print_function

import logging

import kombu_stomp

kombu_stomp.register_transport()

from kombu import Connection

logging.basicConfig(level=logging.DEBUG)

with Connection('stomp://localhost:61613') as conn:
    with conn.SimpleQueue('simple_queue') as queue:
        message = queue.get(block=True, timeout=10)
        message.ack()
        print(message.payload)
