# coding=utf-8
# author="Jianghua Zhao"

import threading
import datetime
import time
import os
import sys
import pickle

from scpy.logger import get_logger

logger = get_logger(__file__)

reload(sys)
sys.setdefaultencoding('utf-8')

lock = threading.Lock()
MAX_LIVE_DAY = 3
MAX_LIVE_COUNT = 500
CLEAN_INTERVAL_SECONDS = 1 * 3600

current_folder = os.path.dirname(os.path.abspath(__file__))
cathe_folder = os.path.join(current_folder, "cathe")
cathe_path = os.path.join(cathe_folder, "url_pool.pkl")


class Singleton(type):
    r_lock = lock = threading.RLock()

    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kw):
        cls.r_lock.acquire()
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kw)
        cls.r_lock.release()
        return cls._instance


class URLPool:
    """
    管理爬过的网页地址
    对每个网页加上时间戳，如果他的存在时间超过最大生命时间，将其删除
    """
    __metaclass__ = Singleton

    def __init__(self):
        self.url_pool = {}
        self.load()
        self.start_clean_pool_thread()

    def __del__(self):
        self.save()

    def add_url(self, channel, url):
        with lock:
            if channel not in self.url_pool:
                self.url_pool[channel] = {}
            self.url_pool[channel][url] = datetime.datetime.now()

    def check_url(self, channel, url):
        if channel in self.url_pool and url in self.url_pool[channel]:
            return True
        return False

    def load(self):
        if os.path.exists(cathe_path):
            try:
                with open(cathe_path, "rb") as f:
                    self.url_pool = pickle.load(f)
            except IOError as ioe:
                logger.exception(ioe)
            except pickle.PickleError as pke:
                logger.exception(pke)

    def save(self):
        if not os.path.exists(cathe_folder):
            os.mkdir(cathe_folder)
        with lock:
            try:
                with open(cathe_path, "wb") as f:
                    pickle.dump(self.url_pool, f)
            except IOError as ioe:
                logger.exception(ioe)
            except pickle.PickleError as pke:
                logger.exception(pke)

    def clear_url_pool(self):
        while True:
            print "clear_url_pool at %s" % str(time.time())
            now = datetime.datetime.now()
            with lock:
                for channel in self.url_pool.keys():
                    items = self.url_pool[channel].items()
                    items = sorted(items, key=lambda x: x[1])
                    for i in range(len(items) - MAX_LIVE_COUNT):
                        key, value = items[i]
                        if value < now - datetime.timedelta(days=MAX_LIVE_DAY):
                            del self.url_pool[channel][key]
            self.save()
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
