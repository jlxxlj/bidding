#! /usr/bin/env python  
# -*- coding:utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from scpy.rabbit_asy_producer import AsyPublisher
import json
import pika
import datetime
from conf import config


def getDateList():
    format = '%Y-%m-%d'
    start_date = datetime.datetime.strptime('2016-03-01', format)
    end_date = datetime.datetime.strptime('2016-08-26', format)
    days = (end_date - start_date).days
    print days
    for day in range(days):
        day_str = start_date + datetime.timedelta(days=day)
        day_str = day_str.strftime(format)
        yield day_str


class CcgpProducer(AsyPublisher):
    def publish_message(self):
        for msg in getDateList():
            msg = {'key': msg}
            properties = pika.BasicProperties(app_id='example-publisher',
                                              content_type='application/json',
                                              headers=msg)
            self._channel.basic_publish(
                '',
                self.QUEUE,
                json.dumps(msg, properties),
            )


if __name__ == '__main__':
    amqp_url = config.AMQP_URL
    producer = CcgpProducer(amqp_url=amqp_url, queue_name='ccgp')
    producer.run()
