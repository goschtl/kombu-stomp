import json
import logging

import pytest
import stomp
from kombu import Connection
from kombu import Exchange
from kombu import Queue

import kombu_stomp

kombu_stomp.register_transport()

logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def jms_map_json(queue):
    stomp_connection = stomp.connect.StompConnection10()
    stomp_connection.start()
    stomp_connection.connect(wait=True)
    body = {"map": {"entry": {"string": ["key", "value"]}}}
    stomp_connection.send('/queue/' + queue.queue.name, json.dumps(body), transformation='jms-map-json')
    return {"key": "value"}

@pytest.fixture
def custom_headers(queue):
    headers = {"custom": "value"}
    stomp_connection = stomp.connect.StompConnection10()
    stomp_connection.start()
    stomp_connection.connect(wait=True)
    stomp_connection.send('/queue/' + queue.queue.name, '', headers=headers)
    return headers


@pytest.fixture
def connection(request):
    _connection = Connection('stomp://localhost:61613').__enter__()
    request.addfinalizer(_connection.__exit__)
    return _connection


@pytest.fixture
def queue(connection):
    return connection.SimpleQueue('test1', serializer='json')


@pytest.fixture
def topic_exchange():
    return Exchange('test', 'topic', durable=True)


def test_json_transformation(jms_map_json, queue):
    """
    GIVEN: a JMX message of type map sent to a queue
    WHEN: it is fetched from the queue
    THEN: it is translated into json
    """
    message = queue.get(block=True, timeout=5)
    message.ack()
    assert message.payload == jms_map_json


def test_headers(custom_headers, queue):
    """
    GIVEN: a message with custom headers sent to a queue
    WHEN: it is fetched from the queue
    THEN: the headers are accessible from the message class
    """
    message = queue.get(block=True, timeout=5)
    message.ack()
    assert message.headers['custom'] == custom_headers['custom']


def test_topic(connection, topic_exchange):
    """
    GIVEN: a topic exchange
    WHEN: a message is sent to a topic
    THEN: it is received back
    """
    test_queue = Queue(topic_exchange.name, exchange=topic_exchange)
    received = []

    def notify(body, message):
        message.ack()
        received.append(message)

    with connection.Consumer(test_queue, callbacks=[notify]) as consumer:
        producer = connection.Producer(serializer='json')
        payload = {'name': '/tmp/lolcat1.avi', 'size': 1301013}
        producer.publish(payload, exchange=topic_exchange, declare=[test_queue])

        while len(received) == 0:
            connection.drain_events()

        assert received[0].payload == payload
