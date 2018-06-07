# coding=utf-8
# author="Jianghua Zhao"

import time
import json
import base64
from util import *

from scpy.xawesome_crawler import BaseCrawler
from scpy.logger import get_logger
from scpy.date_extractor import extract_first_date

from page_parser import get_matched_parser
from queue import get_message, publish_message

import url_pool
import page_start
from content_saver import ContentSaverFactory, DBType

logger = get_logger(__file__)

URL_POOL = url_pool.URLPool()
CONTENT_SAVER = ContentSaverFactory.create(DBType.AWS_S3)


def _store_contents(contents):
    for content in contents:

        # 过滤掉爬取过程中的临时变量
        for key in content.keys():
            if key not in ANNOUNCE_PROPERTY_LIST:
                del content[key]

        CONTENT_SAVER.save(content)


def _check_links(links):
    checked_links = []

    # 删除已经爬取了的网页地址
    for link in links:
        if not URL_POOL.check_url(link[UNI_ORIGIN_ID], link[URL]):
            checked_links.append(link)

    # 判断这个目录页是否已经被爬取
    if len(checked_links) == 1:
        if CRAWLED_COUNT in checked_links[0]:
            checked_links[0][CRAWLED_COUNT] += 1
            # 如果这个目录已经被爬取的次数大于等于 3 次，则不再继续爬取
            if checked_links[0][CRAWLED_COUNT] >= 3:
                checked_links = []
        else:
            checked_links[0][CRAWLED_COUNT] = 1
    else:
        for i in range(len(checked_links)):
            checked_links[i][CRAWLED_COUNT] = 0

    return checked_links


def _check_published_ts(links, start_ts, end_ts):
    checked_links = []
    start_ts = extract_first_date(start_ts)
    end_ts = extract_first_date(end_ts)

    for link in links:
        if PUBLISHED_TS in link:
            publish_ts = extract_first_date(link.get(PUBLISHED_TS))
            if publish_ts and start_ts and publish_ts < start_ts:
                continue
        checked_links.append(link)

    # 判断是否是否继续向后爬
    if len(checked_links) == 1:
        if BEYOND_TIME_COUNT in checked_links[0]:
            checked_links[0][BEYOND_TIME_COUNT] += 1
            # 如果这个目录已经被爬取的次数大于等于 3 次，则不再继续爬取
            if checked_links[0][BEYOND_TIME_COUNT] >= 3:
                checked_links = []
        else:
            checked_links[0][BEYOND_TIME_COUNT] = 1
    else:
        for i in range(len(checked_links)):
            checked_links[i][BEYOND_TIME_COUNT] = 0

    checked_links, links = [], checked_links
    for link in links:
        if PUBLISHED_TS in link:
            publish_ts = extract_first_date(link.get(PUBLISHED_TS))
            if publish_ts and end_ts and publish_ts > end_ts:
                continue
        checked_links.append(link)

    return checked_links


def _filter_links(links):
    filtered_links = []
    for link in links:
        for key in TMP_VARIABLE_LIST:
            if key in link:
                del link[key]
        filtered_links.append(link)
    return filtered_links


class BidCrawler(BaseCrawler):
    sleep_time = 1  # 休眠时间

    def __init__(self, msg_queue,
                 is_monitor=False,  # 是否是定时监控
                 check_published_ts=False,  # 是否检查网页发布时间
                 start_ts="2000-01-01",  # 爬取网页发布时间的起始时间
                 end_ts="",  # 爬取网页发布时间的结束时间
                 skip_parse_failure=False,  # 是否跳过解析错误
                 flip_page_type=0):  # 翻页方式 (0: 依次查找下一页，主要用于监控; 1: 一次产生全部的页，主要用于全量)
        super(BidCrawler, self).__init__()
        self.msg_queue = msg_queue
        self.is_monitor = is_monitor
        self.check_published_ts = check_published_ts
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.skip_parse_failure = skip_parse_failure
        self.flip_page_type = flip_page_type

    def crawl(self):
        # 获取一个消息
        pre_information = get_message(self.msg_queue)
        if pre_information is None:
            return "NO_MESSAGE", {}

        # 获取需要爬取的网页地址
        if DATA_URL in pre_information:
            url = pre_information[DATA_URL]
        else:
            url = pre_information[URL]

        # 设置爬虫浏览目录页方式
        if self.flip_page_type == 1 and not pre_information.get(GENERATE_ALL_PAGE):
            pre_information[GENERATE_ALL_PAGE] = True

        # 获取与url相匹配的parser
        matched_parser = get_matched_parser(url)
        if matched_parser is None:
            return "NO_PARSER", pre_information
        re_url, func = matched_parser

        # 如果需要休眠，则爬虫进行休眠
        sleep_second = pre_information.get(SLEEP_SECOND, 0)
        sleep_second += pre_information.get(SLEEP_FOR_CONTENT, 0)
        if sleep_second > 0:
            time.sleep(sleep_second)

        # 获取网页内容
        method = pre_information.get(METHOD, "GET").upper()
        if method == "POST":
            params = pre_information.get(PARAMS, {})
            html = self.post(url, data=params, timeout=40)
        else:
            html = self.get(url, timeout=60)
        if html is None:
            if NO_CONTENT_TIMES not in pre_information:
                pre_information[NO_CONTENT_TIMES] = 0
                pre_information[SLEEP_FOR_CONTENT] = 0
            if pre_information[NO_CONTENT_TIMES] < 3:
                pre_information[NO_CONTENT_TIMES] += 1
                pre_information[SLEEP_FOR_CONTENT] += 4
                publish_message(self.msg_queue, pre_information)
            return "NO_CONTENT", pre_information
        else:
            pre_information[NO_CONTENT_TIMES] = 0
            pre_information[SLEEP_FOR_CONTENT] = 0

        # 解析网页获取继续访问的链接和已经解析成功的公告内容
        try:
            links, contents = func(html, pre_information)
        except KeyboardInterrupt as e:
            raise e
        except Exception, exception:
            import traceback
            traceback.print_exc(exception)
            logger.error("Parse html failed. %s\n%s" % (exception.message,
                                                        json.dumps(pre_information).decode("unicode-escape")))
            return "PARSER_ERROR", pre_information

        # 并处理解析后的结果
        if self.is_monitor:
            for cont in contents:
                URL_POOL.add_url(cont[UNI_ORIGIN_ID], cont[URL])
            links = _check_links(links)

        if self.check_published_ts:
            links = _check_published_ts(links, self.start_ts, self.end_ts)
        links = _filter_links(links)

        _store_contents(contents)
        publish_message(self.msg_queue, links)
        return "SUCCESS", pre_information

    def run(self):
        while True:
            res, info = self.crawl()

            if res is "NO_MESSAGE":
                if self.sleep_time > 64:
                    logger.info("NO_MESSAGE: There is no more message to consume and the crawler is stopped!")
                    break
                else:
                    logger.info("NO_MESSAGE: The crawler is sleeping for {0} seconds".format(self.sleep_time))
                    time.sleep(self.sleep_time)
                    self.sleep_time *= 2
            elif res is "SUCCESS":
                self.sleep_time = 1
                logger.info("SUCCESS: %s" % json.dumps({"url": info.get(URL)}))
            elif res is "PARSER_ERROR":
                if not self.skip_parse_failure:
                    break
            else:
                logger.info("%s: %s" % (res, json.dumps(info).decode("unicode-escape")))




# def run_crawler(crawler):
#     while True:
#         res = crawler.crawl()
#
#         if res is "NO_MESSAGE":
#             if crawler.sleep_time > 64:
#                 logger.info("There is no more message to consume and the crawler is stopped!")
#                 break
#             else:
#                 logger.info("crawler is sleeping for {0} seconds".format(crawler.sleep_time))
#                 time.sleep(crawler.sleep_time)
#                 crawler.sleep_time *= 2
#
#         elif res is "NO_PARSER":
#             logger.info("NO_PARSER")
#
#         elif res is "NO_CONTENT":
#             logger.info("NO_CONTENT")
#
#         else:
#             crawler.sleep_time = 1
#             logger.info("SUCCESS")


if __name__ == "__main__":
    # start_information = page_start.start_urls
    #
    # publish_message(start_information)
    #
    # bid_crawler = BidCrawler()
    # 
    # bid_crawler.run()

    logger.info('qqqq')
