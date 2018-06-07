#! /usr/bin/env python  
# -*- coding:utf-8 -*-

"""
RabbitMq 工具封装

__author__="wu.zheng"
"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from rabbit_consumer_asy import AsyConsumer


def consumer(queue_name, task_func):
    """

    params:
    queue_name : name of queue
    task_func :  具体的爬虫任务, 数据存储之类
    """
    consumer_cl = AsyConsumer(queue_name=queue_name, consume_func=task_func)
    try:
        consumer_cl.run()
    except (KeyboardInterrupt, SystemExit):
        consumer_cl.stop()
        return

