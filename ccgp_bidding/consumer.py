#! /usr/bin/env python  
# -*- coding:utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from queue import rabbitmq
from crawl import crawl
import json


def task(body):
    param = json.loads(body)
    crawl_param = param.get('key')
    crawl.crawl(crawl_param, force_parse=True)


if __name__ == '__main__':
    rabbitmq.consumer('ccgp', task)
