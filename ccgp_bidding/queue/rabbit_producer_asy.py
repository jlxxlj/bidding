#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pika
import json

from scpy.logger import get_logger

logger = get_logger(__file__)


class AsyPublisher(object):
    def __init__(self, amqp_url, queue_name):

        self.QUEUE = queue_name
        self._connection = None
        self._channel = None
        self._deliveries = []
        self._acked = 0
        self._nacked = 0
        self._message_number = 0
        self._stopping = False
        self._url = amqp_url
        self._closing = False

    def connect(self):
        return pika.SelectConnection(pika.URLParameters(self._url),
                                     self.on_connection_open,
                                     stop_ioloop_on_close=False)

    def on_connection_open(self, unused_connection):
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):

        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            self._connection.add_timeout(5, self.reconnect)

    def reconnect(self):
        logger.info('reconnect')
        self._deliveries = []
        self._acked = 0
        self._nacked = 0
        self._message_number = 0
        self._connection.ioloop.stop()
        self._connection = self.connect()
        self._connection.ioloop.start()

    def open_channel(self):
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_queue(self.QUEUE)

    def add_on_channel_close_callback(self):
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        # todo channel 被关闭的时候, 会关闭collection
        if not self._closing:
            self._connection.close()

    def setup_queue(self, queue_name):
        self._channel.queue_declare(self.on_queue_declareok, queue_name, durable=True)

    def on_queue_declareok(self, method_frame):

        self.start_publishing()

    def start_publishing(self):

        self.publish_message()

    def enable_delivery_confirmations(self):
        self._channel.confirm_delivery(self.on_delivery_confirmation)

    def on_delivery_confirmation(self, method_frame):

        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        if confirmation_type == 'ack':
            self._acked += 1
        elif confirmation_type == 'nack':
            self._nacked += 1
        self._deliveries.remove(method_frame.method.delivery_tag)

    def schedule_next_message(self):

        if self._stopping:
            return

        self._connection.add_timeout(self.PUBLISH_INTERVAL,
                                     self.publish_message)

    def publish_message(self):

        """发送消息
        做是否停止的判断
        if self._stopping:
            return
        """
        raise NotImplementedError

    def close_channel(self):
        if self._channel:
            self._channel.close()

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        self._stopping = True
        self.close_channel()
        self.close_connection()
        self._connection.ioloop.start()

    def close_connection(self):
        self._closing = True
        self._connection.close()


if __name__ == '__main__':

    amqp_url = 'amqp://sc-admin:1qaz2wsx@192.168.31.114:5672/%2F'


    class MongoProducer(AsyPublisher):
        def publish_message(self):
            for index in range(100000):
                message = {'key': index}
                print message
                properties = pika.BasicProperties(app_id='example-publisher',
                                                  content_type='application/json',
                                                  headers=message
                                                  )
                self._channel.basic_publish(
                    '',
                    self.QUEUE,
                    json.dumps(message),
                    properties)
                if index % 10 == 0:
                    logger.info(index)


    producer = MongoProducer(amqp_url, queue_name='test_p')
    print producer.QUEUE
    try:
        producer.run()
    except KeyboardInterrupt:
        producer.stop()
