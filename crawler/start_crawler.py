# coding=utf-8
# author="Jianghua Zhao"

import sys, getopt
from threading import Thread

from scpy.logger import get_logger
from policy import Policy

from crawler_runner import BidRunner
from page_start import start_urls
import queue
from util import *

logger = get_logger(__file__)


def do_filter(infos, filters):
    res = []

    origin_region = filters.get(ORIGIN_REGION)
    url = filters.get(URL)
    for info in infos:
        check_region = origin_region is None or origin_region in info.get(ORIGIN_REGION)
        check_url = url is None or url in info.get(URL)
        if check_region and check_url:
            res.append(info)

    return res


def start_crawlers(policy):
    logger.info("Start crawling")
    queue_prefix = "bidding_msg_queue"

    st_urls = do_filter(start_urls, policy.START_FILTER)

    queue_list = []
    msgs = {}
    if policy.START_POLICY == 0:
        queue_name = queue_prefix
        for st_url in st_urls:
            if queue_name not in msgs:
                queue_list.append(queue_name)
                msgs[queue_name] = []
            msgs[queue_name].append(st_url)

    elif policy.START_POLICY == 1:
        for st_url in st_urls:
            region_code = BID_REGION_CODE_TABLE[st_url[ORIGIN_REGION].split('>>')[0]]
            queue_name = "_".join((queue_prefix, region_code))

            if queue_name not in msgs:
                queue_list.append(queue_name)
                msgs[queue_name] = []
            msgs[queue_name].append(st_url)

    elif policy.START_POLICY == 2:
        for st_url in st_urls:
            region_code = BID_REGION_CODE_TABLE[st_url[ORIGIN_REGION].split('>>')[0]]
            website_addr = get_host_address(st_url[URL])
            queue_name = "_".join((queue_prefix, region_code, website_addr))

            if queue_name not in msgs:
                queue_list.append(queue_name)
                msgs[queue_name] = []
            msgs[queue_name].append(st_url)

    elif policy.START_POLICY == 3:
        for st_url in st_urls:
            region_code = BID_REGION_CODE_TABLE[st_url[ORIGIN_REGION].split('>>')[0]]
            website_addr = get_host_address(st_url[URL])
            queue_name = "_".join((queue_prefix, region_code, website_addr))
            count = len([name for name in queue_list if name.startswith(queue_name)])
            queue_name += "_%s" % count

            if queue_name not in msgs:
                queue_list.append(queue_name)
                msgs[queue_name] = []
            msgs[queue_name].append(st_url)

    if len(queue_list) == 1:
        bid_runner = BidRunner(queue_name, msgs[queue_name], policy)
        bid_runner.run()
    elif len(queue_list) > 1:
        thread_list = []
        for queue_name in queue_list:
            bid_runner = BidRunner(queue_name, msgs[queue_name], policy)
            thread = Thread(target=bid_runner.run)
            thread_list.append(thread)
            # thread.setDaemon()
            thread.start()

        # 等待所有子线程结束
        for thread in thread_list:
            thread.join()
    logger.info("End crawling")


def usage():
    print "Usage:"
    print "\tpython start_crawler.py [options]\n"
    print "Options:"
    print "\t--policy=<policy_file>     \tpolicy file"
    print """\t--policy_type=<policy_type>\tpolicy type
                                    \t# 爬虫启动策略
                                    \t# 0. 启动一个Queue负责所有的消息
                                    \t# 1. 每个省启动一个Queue负责每个省的所有消息
                                    \t# 2. 每个网站启动一个Queue负责每个网站的所有消息
                                    \t# 3. 每个源启动一个Queue负责每个源的所有消息
    """
    print "\t--crawler_type=<type>      \tcrawler type(1:全量爬取, 2:定时爬取), default is 1"
    print "\t--crawler_number=<number>  \tset the thread number of crawler, default is 3"
    print "\t--filter_region=<region>   \tset the origin region to crawl "
    print "\t--filter_url=<url>         \tset the url to crawl"
    print "\t--apply_time_interval      \tset crawler will check the announce publish time"
    print "\t--time_st=<start_time>     \tset time interval's start, default is 30 days before"
    print "\t--time_ed=<end_time>       \tset time interval's end"
    print "\t-h, --help                 \tshow script usage"
    print ""


if __name__ == "__main__":
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "h",
                               ["policy=", "crawler_type=", "crawler_number=", "filter_region=", "filter_url=",
                                "apply_time_interval", "time_st=", "time_ed=", "help"])

    crawl_policy = Policy()
    argv, show_help = [], False
    for op, value in opts:
        if op == "--policy":
            argv.append(value)
        if op == "--crawler_type":
            try:
                value = int(value)
                crawl_policy.CRAWLER_TYPE = int(value)
                argv.append(value)
            except Exception, e:
                print e.message
                exit(1)
        if op == "--crawler_number":
            try:
                value = int(value)
                crawl_policy.CRAWLER_NUMBER = value
                argv.append(value)
            except Exception, e:
                print e.message
                exit(1)
        if op == "--filter_region":
            crawl_policy.START_FILTER[ORIGIN_REGION] = unicode(value)
            argv.append(value)
        if op == "--filter_url":
            crawl_policy.START_FILTER[URL] = value
            argv.append(value)
        if op == "--apply_time_interval":
            crawl_policy.APPLY_TIME_INTERVAL = True
            argv.append(value)
        if op == "--time_st":
            try:
                datetime.datetime.strptime(value, "%Y-%m-%d")
                crawl_policy.TIME_INTERVAL_ST = value
                argv.append(value)
            except Exception, e:
                print e.message
                exit(1)
        if op == "--time_ed":
            try:
                datetime.datetime.strptime(value, "%Y-%m-%d")
                crawl_policy.TIME_INTERVAL_ED = value
                argv.append(value)
            except Exception, e:
                print e.message
                exit(1)
        if op == "-h" or op == "--help":
            show_help = True
            argv.append(value)
    if len(argv) == 0 or show_help:
        usage()

    if len(argv) > 0:
        start_crawlers(crawl_policy)
    # start_crawlers(crawl_policy)
