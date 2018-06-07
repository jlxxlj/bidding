# coding=utf-8
# author="Jianghua Zhao"

"""
负责按启动策略启动爬虫
"""

import queue
import datetime
import time
from threading import Thread
import random

from scpy.logger import get_logger
from crawler import BidCrawler
import url_pool

from util import MAX_CRAWLER_NUMBER

logger = get_logger(__file__)


class BidRunner(object):
    """
    爬虫启动器：
    按用户配置的 policy， 对爬虫进行启动
    一个启动器只负责一个 queue 下的爬虫的启动
    """

    def __init__(self, queue_name, msg, policy):
        self.queue_name = queue_name
        self.msg = msg
        self.policy = policy

    def run(self):
        is_monitor = (self.policy.CRAWLER_TYPE == 2)  # 是否是定时监控
        schedule_seconds = self.policy.SCHEDULE_TIME  # 监控定时
        for idx, sec in enumerate(schedule_seconds):
            schedule_seconds[idx] += random.randint(-1700, 1700)
        schedule_seconds = sorted(schedule_seconds)
        schedule_seconds.append(24 * 3600 + schedule_seconds[0])

        while True:
            thread_list = []
            queue.publish_message(self.queue_name, self.msg)

            crawler_number = self.policy.CRAWLER_NUMBER
            for m in self.msg:
                if m.get(MAX_CRAWLER_NUMBER) and m.get(MAX_CRAWLER_NUMBER) < crawler_number:
                    crawler_number = m.get(MAX_CRAWLER_NUMBER)

            try:
                for i in range(crawler_number):
                    crawler = BidCrawler(msg_queue=self.queue_name,
                                         is_monitor=is_monitor,
                                         check_published_ts=self.policy.APPLY_TIME_INTERVAL,
                                         start_ts=self.policy.TIME_INTERVAL_ST,
                                         end_ts=self.policy.TIME_INTERVAL_ED,
                                         skip_parse_failure=True)
                    thread = Thread(target=crawler.run)
                    thread.start()
                    thread_list.append(thread)

                for thread in thread_list:
                    thread.join()

                if is_monitor:
                    now = datetime.datetime.now()
                    seconds_of_day = (now.hour * 3600 + now.minute * 60 + now.second)
                    for second in schedule_seconds:
                        if second > seconds_of_day:
                            sleep_seconds = second - seconds_of_day
                            logger.info("The crawler will be started after %s seconds." % sleep_seconds)
                            time.sleep(sleep_seconds)
                            break
                else:
                    break
            except KeyboardInterrupt, e:
                print e.message
                break

        # 缓存所有爬过的url
        url_pool.URLPool().save()


if __name__ == "__main__":
    from util import *
    from policy import Policy

    policy = Policy()
    policy.CRAWLER_NUMBER = 1

    msg = [{ORIGIN_REGION: u"广西",
            URL: "http://www.gxgp.gov.cn/zbxjcg/index.htm",
            ANNOUNCE_TYPE: u"中标公告",
            PURCHASE_TYPE: u"询价采购",
            NOTE: u"广西壮族自治区政府采购中心-询价采购"}]

    runner = BidRunner("test", msg=msg, policy=policy)
    runner.run()

    pass
