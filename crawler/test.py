# coding=utf-8
# author="Jianghua Zhao"

import crawler
import queue
from util import *
import policy
import start_crawler


def test_crawler():
    info = [{URL: "http://www.hljcg.gov.cn/xwzs!index.action"},
            {ORIGIN_REGION: u"黑龙江",
                                                                URL: "http://www.hljcg.gov.cn/xwzs!queryXwxxqx.action?lbbh=5&xwzsPage.pageNo=1",
                                                                ANNOUNCE_TYPE: u"成交公告",
                                                                NOTE: u"黑龙江省政府采购网-成交公告"}
            ]

    queue.publish_message("test", info)

    bid_crawler = crawler.BidCrawler("test")
    bid_crawler.run()


def test_start_crawler():
    plc = policy.Policy()
    plc.CRAWLER_TYPE = 2
    plc.CRAWLER_NUMBER = 1
    plc.APPLY_TIME_INTERVAL = True
    plc.START_FILTER[URL] = "www.gdgpo.gov.cn"

    start_crawler.start_crawlers(plc)


def test_url_pool():
    import url_pool

    a = url_pool.URLPool()
    a.add_url("aaaa")
    b = url_pool.URLPool()
    b.add_url("bbbb")
    c = url_pool.URLPool()
    c.add_url("cccc")
    d = url_pool.URLPool()
    d.add_url("dddd")

    print d.url_pool

    import time
    time.sleep(20)
    print d.url_pool


if __name__ == "__main__":
    test_crawler()
    # test_start_crawler()
