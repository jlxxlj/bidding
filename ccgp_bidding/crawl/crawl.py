#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import datetime

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
print sys.path
import requests
import copy
from scpy.logger import get_logger
import request_tool
import parse.parse as parse
from db.db_helper import *
from url_pool import URLPool
import json
from conf import config
import base64

logger = get_logger(__file__)
old_search_url = 'http://search.ccgp.gov.cn/dataBidOld.jsp?'
new_search_url = 'http://search.ccgp.gov.cn/dataB.jsp?'

search_para = {
    'searchtype': 0,
    'page_index': 1,
    'bidSort': 0,
    'buyerName': '',
    'projectId': '',
    'pinMu': 0,
    'bidType': 11,
    'dbselect': 'bidx',
    'kw': '',
    'start_time': '',
    'end_time': '',
    'timeType': 6,
    'displayZone': '',
    'zoneId': '',
    'agentName': ''
}
validTypes = {'bid_announce': 7, 'deal_announce': 11}

session = requests.session()
TIMEOUT = 60

db_bid_source = None
db_bid_analysis_result = None


def save_bid_source(url, html, region, website):
    global db_bid_source

    if config.SOURCE_CODE_SAVE_MODE == 0:
        source_code = {"url": url, "html": html}
        if db_bid_source is None:
            db_bid_source = DBHelper(DBType.MONGO)
        db_bid_source.insert("bid_source", source_code)
    else:
        # path = "bidding/<region>/<website>/2016/10/13/file_name"
        now = datetime.datetime.now()
        date_path = now.strftime("%Y/%m/%d")
        file_name = base64.b64encode(url)
        file_name = u"/".join((region, website, date_path, file_name))

        if db_bid_source is None:
            db_bid_source = DBHelper(DBType.S3)

        db_bid_source.insert("sc-bidding", {"html": html, "file_name": file_name})
        logger.info("save data to s3 success")


announce_keys = ["purchaser", "purchase_agent", "purchase_category", "title", "url", "region", "published_ts",
                 "announced_ts", "winning_ts", "announce_type", "amount", "unit", "currency"]
result_keys = ["winning_company", "winning_amount", "unit", "currency"]


def save_bid_analysis_result(announce_data):
    global db_bid_analysis_result

    # 过滤掉没用的值
    for key, value in announce_data.items():
        if key not in announce_keys + ["analysis_result"]:
            del announce_data[key]
        elif value is None or (isinstance(value, (str, unicode)) and len(value) == 0):
            del announce_data[key]

    analysis_result = announce_data.get("analysis_result")
    if analysis_result is None:
        return
    del announce_data["analysis_result"]

    winning_ts = announce_data.get("winning_ts")
    if winning_ts is None or winning_ts == "":
        announce_data["winning_ts"] = analysis_result["bid_time"]

    if db_bid_analysis_result is None:
        db_bid_analysis_result = postgresql_sc.PostgresqlUtil()

    update_condition = {"url": announce_data.get("url")}
    db_bid_analysis_result.update(table_name="bidding_announce", dict_data=announce_data,
                                  dict_condition=update_condition,
                                  upsert=True)

    res = db_bid_analysis_result.select(table_name="bidding_announce", dict_condition=update_condition)
    bidding_announce_id = res[0][0]
    delete_condition = {"bidding_announce_id": bidding_announce_id}
    db_bid_analysis_result.delete(table_name="bidding_result", dict_condition=delete_condition)

    bid_result = analysis_result.get("bid_result")
    for i in range(len(bid_result)):
        result = bid_result[i]
        for key, value in result.items():
            if key not in result_keys:
                del analysis_result[key]
            elif value is None or (isinstance(value, (str, unicode)) and len(value) == 0):
                del result[key]
        bid_result[i] = result

    for com in bid_result:
        if com.get("winning_company") is None:
            continue
        com["bidding_announce_id"] = bidding_announce_id
        db_bid_analysis_result.insert("bidding_result", com)

    logger.info("write an analysis result (%s)." % announce_data.get("url"))


def dateTrans(date):
    tmpList = date.split('-')
    return '%s:%s:%s' % (tmpList[0], tmpList[1], tmpList[2])


def crawl_detail(item_list, force_parse=False):
    """
    crawl detail information
    :param item_list: item list for crawling
    :param force_parse: force crawl urls which have been crawled
    :return:
    """
    for item in item_list:
        detail_url = item.get("url")
        is_crawled = URLPool().check_url(detail_url)

        if is_crawled and force_parse is False:
            logger.info("skip url: %s" % detail_url)
            continue
        else:
            logger.info("craw url: %s" % detail_url)

        res = request_tool.make_request(detail_url, method='GET', params={})
        html = res.content

        parse.parse_detail(html, item)

        extra_seconds = 0
        if item.get("analysis_result").get("bid_result") is not None:
            extra_seconds = 1 * len(item.get("analysis_result").get("bid_result"))

        try_time = 0
        while try_time < 3:
            try:
                session.post(config.TORNADO_SERVICE_URL, data={"announce_data": json.dumps(item)},
                             timeout=TIMEOUT + extra_seconds)
                # save_bid_analysis_result(item)
                break
            except Exception, e:
                logger.info(e)
                try_time += 1

        if try_time < 3:
            try:
                save_bid_source(detail_url, html, region=u"中央", website=u"中国政府采购网")
                URLPool().add_url(detail_url)
            except Exception, e:
                print e
                pass
        else:
            logger.error("%s (url=%s)" % (e.message, item.get("url")))


def crawl(date, force_parse=False):
    for bidType in validTypes.values():
        logger.info('start crawl {0}, bidType {1}'.format(date, str(bidType)))
        tmpSearchPara = copy.deepcopy(search_para)
        tmpSearchPara['bidType'] = bidType
        tDate = dateTrans(date)
        tmpSearchPara['start_time'] = tDate
        tmpSearchPara['end_time'] = tDate

        if tDate < '2013:01:01':
            sign = 'old'
            search_url = old_search_url
            tmpSearchPara['searchtype'] = 1
            logger.info('old url used')
        else:
            sign = 'new'
            search_url = new_search_url
            tmpSearchPara['searchtype'] = 2
            logger.info('new url used')

        res = request_tool.make_request(search_url, params=tmpSearchPara, method='GET')
        html = res.content
        total_page = parse.parse_page_num(html)
        logger.info('total page %d' % total_page)
        item_list = parse.parse_list_page(html, sign=sign)
        crawl_detail(item_list, force_parse)

        if total_page > 1:
            for page in range(2, total_page + 1):
                logger.info('page: %d' % page)
                tmpSearchPara['dbselect'] = 'infox'
                tmpSearchPara['page_index'] = page
                res = request_tool.make_request(search_url, params=tmpSearchPara, method='GET')
                logger.info(res.url)
                html = res.content
                item_list = parse.parse_list_page(html, sign)
                crawl_detail(item_list, force_parse)

    return None


def crawl_bidding_info():
    urls = ["http://www.ccgp.gov.cn/cggg/zygg/zbgg/",  # 中央中标
            "http://www.ccgp.gov.cn/cggg/zygg/cjgg/",  # 中央成交
            "http://www.ccgp.gov.cn/cggg/dfgg/zbgg/",  # 地方中标
            "http://www.ccgp.gov.cn/cggg/dfgg/cjgg/"]  # 地方成交

    for url in urls:
        logger.info("crawl_bidding_info(): %s" % url)
        items = crawl_index(url)
        crawl_detail(items)


def crawl_index(url):
    result = []

    next_page = url
    while next_page:
        logger.info("crawl_index(): %s" % next_page)
        # html = request_tool.selenium_request(next_page, method='GET', params={})
        res = request_tool.make_request(url=next_page, method='GET', params={})
        html = res.content
        items, next_page = parse.parse_announce_list(html, next_page)

        result.extend(items)

    return result


if __name__ == '__main__':
    crawl('2016-05-04')
