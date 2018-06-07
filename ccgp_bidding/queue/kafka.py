#! /usr/bin/env python  
# -*- coding:utf-8 -*-

"""
kafka 工具类
kafka topic 默认都只有一个Partition


__author__="wu.zheng"
"""


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from ..conf import config
from pykafka import KafkaClient
from scpy.logger import get_logger

logger = get_logger(__file__)

class KafkaTool(object):
    """kafka 的一些常用方法封装

    会默认使用本地配置,配置文件详见conf/config.py

    example:
    kafka_tool = KafkaTool('test')

    produce 方法接收一个字符串存入
    for msg in range(100):
        print msg
        kafka_tool.produce(str(msg))

    consume 会产生一个迭代器
    print kafka_tool.topic_size
    for msg in kafka_tool.consume(group='test_1', count=10, reset_offset=True):
        print msg

    """

    client = KafkaClient(hosts=config.KAFKA_HOST)

    def __init__(self, topic_name):
        self.topic = self.client.topics[topic_name]
        self.topic_size = self.get_total_count()
        self.producer = self.topic.get_sync_producer()

    def get_all_topics(self):
        print self.client.topics
        return self.client.topics


    def get_total_count(self):
        """获得topic中所有message 数量, 由于我们应用场景的特点,默认只有一个Partion

        由于 每个topic 只有一个Partion 所以获得
        return: count topic 消息的数量
        """
        count = self.topic.fetch_offset_limits(-1)[0].offset[0]
        return  count

    def produce(self, msg):
        """把消息存入kafka

        params:
        --------
            msg : 消息, 如果是dict or list 需要 json.dumps 后传进来
        """
        if not isinstance(msg, basestring):
            raise Exception(msg, 'msg must unicode or string')

        self.producer.produce(msg)


    def consume(self, group, count=0, reset_offset=False):
        """会产生一个迭代器,返回msg, 消费完了会自动退出

        params:
           group: group id
           count : 需要消费的消息数量,  默认为0, 消费所有消息
           reset_offset: boolean 是否重置group的 offset , 默认为False 从上次commit 的位置开始消费

        """

        consumer = self.topic.get_simple_consumer(consumer_group=group)
        if reset_offset:
            consumer.reset_offsets()

        held_offsets = consumer.held_offsets.get(0)
        held_offsets = 0 if held_offsets==-2 else held_offsets
        print held_offsets

        if held_offsets+1 == self.topic_size:
            logger.info('message is all conssumed ')
            consumer.stop()
            return

        if count == 0:
            count = self.topic_size

        if held_offsets+count>self.topic_size:
            count = self.topic_size - held_offsets

        index = 0
        for msg in consumer:
            if index+1 == count:
                consumer.commit_offsets()
                logger.info('finish consume %d'%count)
                consumer.stop()
                return
            yield msg.value

            consumer.commit_offsets()
            index += 1
        consumer.stop()

        return

