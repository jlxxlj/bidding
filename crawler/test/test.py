# coding=utf-8
# author="Jianghua Zhao"

import crawler
import queue
from util import *
import policy
import start_crawler


def test_crawler():
    info = [{ORIGIN_REGION: u"重庆>>巴南区",
           URL: "http://jy.bnzw.gov.cn/LBv3/n_newslist_zz.aspx?Item=100026",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市巴南区行政服务和公共资源交易中心",
           NOTE: u"重庆市重庆綦江公共资源综合交易网巴南区行政服务和公共资源交易中心-中标公示"}
            ]

    queue.publish_message("test", info)
    bid_crawler = crawler.BidCrawler("test")
    bid_crawler.run()



def test_start_crawler():
    plc = policy.Policy()
    plc.CRAWLER_TYPE = 2
    plc.CRAWLER_NUMBER = 3
    plc.APPLY_TIME_INTERVAL = True
    plc.START_FILTER[URL] = "www.gxzfcg.gov.cn"

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
    test_url_pool()
    # test_start_crawler()
