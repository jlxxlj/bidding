# coding=utf-8
# author="Jianghua Zhao"

import threading
from Queue import Queue

__QUEUES = {}
__publish_lock = threading.Lock()
__get_lock = threading.Lock()


def get_message(queue_name):
    if queue_name in __QUEUES:
        with __get_lock:
            if not __QUEUES[queue_name].empty():
                return __QUEUES[queue_name].get()
            else:
                return None
    else:
        raise Exception("there is not queue named %s" % queue_name)


def publish_message(queue_name, msg):
    if not isinstance(msg, list):
        msg = [msg]
    if len(msg) > 0:
        with __publish_lock:
            if queue_name not in __QUEUES:
                __QUEUES[queue_name] = Queue()
        for item in msg:
            __QUEUES[queue_name].put(item)


def clear_queue(queue_name):
    if queue_name in __QUEUES:
        with __get_lock:
            while not __QUEUES[queue_name].empty():
                __QUEUES[queue_name].get()

