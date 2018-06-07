# coding=utf-8
# author="JianghuaZhao"

import os
import re
import time
import datetime

from scpy.logger import get_logger
# from crawl.crawl import crawl
from send_email import send_warn_email

logger = get_logger(__file__)

DATE_FORMAT = '%Y-%m-%d'
MONITOR_DATE_LENGTH = 2
SCHEDULE_SECONDS = [3 * 3600,
                    6 * 3600,
                    7 * 3600,
                    8 * 3600,
                    9 * 3600,
                    10 * 3600,
                    11 * 3600,
                    12 * 3600,
                    13 * 3600,
                    14 * 3600,
                    15 * 3600,
                    16 * 3600,
                    17 * 3600,
                    18 * 3600,
                    19 * 3600,
                    20 * 3600,
                    21 * 3600,
                    22 * 3600,
                    24 * 3600]
MONITOR_USER_ADDRESS = "309927063@qq.com"


def get_log_file():
    names = os.listdir("./py_log/")
    date = None
    file_name = None
    for name in names:
        d = re.findall("\d{4}-\d{2}-\d{2}", name)[0]
        d = datetime.datetime.strptime(d, DATE_FORMAT)
        if date is None or date < d:
            date = d
            file_name = name
    return file_name


def on_schedule():
    now = datetime.datetime.now()
    seconds_of_day = (now.hour * 3600 + now.minute * 60 + now.second)
    for second in SCHEDULE_SECONDS:
        if second > seconds_of_day:
            sleep_seconds = second - seconds_of_day
            time.sleep(sleep_seconds)
            break


def monitor_bid_announce():
    try_times = 0
    while True:
        import crawl.crawl
        reload(crawl.crawl)

        date = time.strftime(DATE_FORMAT, time.localtime(time.time()))
        current_date = datetime.datetime.strptime(date, DATE_FORMAT)
        datedelta = 0
        while datedelta < MONITOR_DATE_LENGTH:
            date = current_date - datetime.timedelta(days=datedelta)
            date_str = date.strftime(DATE_FORMAT)
            try:
                crawl.crawl.crawl(date_str)
                try_times = 0
                logger.info(u"end crawl {0}".format(date_str))
            except Exception, e:
                try_times += 1
                logger.error(e.message)
                if try_times <= 3:
                    logger.info(u"the {0}st time to restart crawl".format(try_times))
                    continue
                else:
                    break
            datedelta += 1

        if try_times > 3:
            logger.error(u"the process stopped for multi-time failed to crawl")
            file_name = get_log_file()
            if file_name is not None:
                log_file = "./py_log/" + file_name
                send_warn_email(MONITOR_USER_ADDRESS, log_file)
            break

        on_schedule()


def monitor_bid_announce_2():
    try_times = 0
    while True:
        import crawl.crawl
        reload(crawl.crawl)

        try:
            logger.info(u"start crawl")
            crawl.crawl.crawl_bidding_info()
            logger.info(u"end crawl")
            try_times = 0
        except Exception, e:
            try_times += 1
            logger.error(e.message)
            if try_times <= 3:
                logger.info(u"the {0}st time to restart crawl".format(try_times))
                continue

        if try_times > 3:
            logger.error(u"the process stopped for multi-time failed to crawl")
            file_name = get_log_file()
            if file_name is not None:
                log_file = "./py_log/" + file_name
                send_warn_email(MONITOR_USER_ADDRESS, log_file)
            break

        on_schedule()

if __name__ == "__main__":
    # monitor_bid_announce()
    monitor_bid_announce_2()
