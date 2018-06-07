# coding=utf-8
# author="Jianghua Zhao"

import threading
import datetime
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

lock = threading.Lock()
MAX_LIVE_DAY = 1
CLEAN_INTERVAL_SECONDS = 3600


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kw)
        return cls._instance


class URLPool:
    """
    管理爬过的网页地址
    对每个网页加上时间戳，如果他的存在时间超过最大生命时间，将其删除
    """
    __metaclass__ = Singleton

    def __init__(self):
        self.url_pool = {}
        self.start_clean_pool_thread()

    def add_url(self, url):
        with lock:
            self.url_pool[url] = datetime.datetime.now()

    def check_url(self, url):
        return url in self.url_pool

    def clear_url_pool(self):
        while True:
            print "clear_url_pool at %s" % str(time.time())
            now = datetime.datetime.now()
            with lock:
                for key, value in self.url_pool.items():
                    if value < now - datetime.timedelta(days=MAX_LIVE_DAY):
                        del self.url_pool[key]

            URLPool.on_schedule()

    def start_clean_pool_thread(self):
        thread = threading.Thread(target=self.clear_url_pool)
        thread.setDaemon(True)
        thread.start()

    @staticmethod
    def on_schedule():
        now_time = datetime.datetime.now()
        now_time_at_second = now_time.hour * 3600 - now_time.minute * 60 - now_time.second
        sleep_seconds = CLEAN_INTERVAL_SECONDS - now_time_at_second % CLEAN_INTERVAL_SECONDS
        time.sleep(sleep_seconds)
