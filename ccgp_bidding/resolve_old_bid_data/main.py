# coding=utf-8
# author="Jianghua Zhao"

import json
import requests
import re
import datetime
import sys

sys.path.append("../")

from scpy.logger import get_logger
from conf import config
from db import mongo_sc
from crawl.parse import find_all_info
from crawl.parse import html_preprocess
from crawl.parse import html_analysis
from crawl.parse import parse

logger = get_logger(__file__)

TIMEOUT = 30
BID_PROPERTY = [""]


def analysis_bid_summary(summary):
    """
    解析summary中的字段：招标公告日期、公告时间、中标日期、总中标金额、单位、货币
    :param html:
    :return:
    """
    res = {}

    time = summary.get(u"本项目招标公告日期")
    if time is not None:
        time = time.strip()
        if re.match(u"2\d{3}年\d{1,2}月\d{1,2}日", time):
            res["announced_ts"] = find_all_info.regular_time(time)

    time = summary.get(u"中标日期")
    if time is None:
        time = summary.get(u"成交日期")
    if time is not None:
        time = time.strip()
        if re.match(u"2\d{3}年\d{1,2}月\d{1,2}日", time):
            res["winning_ts"] = find_all_info.regular_time(time)

    text = summary.get(u"总中标金额")
    if text is None:
        text = summary.get(u"总成交金额")
    if text is not None:
        text = text.strip()
        if re.search(u"(?:￥|$|)\d+(?:\.\d+|).{1,3}（.{1,5}）", text) is not None:
            amount = re.findall("\d+(?:\.\d+|)", text)[0]
            res["amount"] = float(amount)
            texts = re.split(u"{0}|（|）".format(amount), text)
            res["unit"] = texts[1]
            res["currency"] = texts[2]

    category = summary.get(u"品目")
    if category is not None and len(category) > 0:
        res["purchase_category"] = category

    purchaser = summary.get(u"采购单位")
    if purchaser is not None and len(purchaser) > 0 and purchaser != u"详见公告正文":
        res["purchaser"] = purchaser

    agent = summary.get(u"代理机构名称")
    if agent is not None and len(agent) > 0 and agent != u"详见公告正文":
        res["purchase_agent"] = agent

    return res


def analysis_bid_announce(html, item):
    announce_type = item.get("announce_type")
    if announce_type in [u"中标公告", u"成交公告", u"竞价结果"]:
        content_html = html_preprocess.html_purify(html)
        doc = html_analysis.analysis_html(content_html)
        result = find_all_info.find_all_info(doc)

        if len(result.get("bid_result")) == 0:
            content_html = html_preprocess.build_beautifulsoup(content_html).prettify()
            content_html = html_preprocess.build_beautifulsoup(content_html).get_text()
            result = find_all_info.find_all_info([content_html])
    else:
        result = {"bid_time": "", "bid_result": []}

    time = result.get("bid_time")
    if len(time) == 0:
        time = item.get("published_ts")
        if "." in time:
            time = re.findall("\d{4}\.\d{1,2}\.\d{1,2}", time)[0]
            y, m, d = time.split(".")
        elif "-" in time:
            time = re.findall("\d{4}\-\d{1,2}\-\d{1,2}", time)[0]
            y, m, d = time.split("-")
        else:
            return result
        time = datetime.date(year=int(y), month=int(m), day=int(d))
        time = time.strftime("%Y-%m-%d")
        result["bid_time"] = time

    return result


def main():
    session = requests.session()

    mongo_util = mongo_sc.MongoUtil()
    bid_source = mongo_util.get_coll(db_name="bid_data", collection="merged_announce")

    count = 0
    skip_count = 334422
    total_count = bid_source.count()
    ids = []
    logger.info("collect all _ids start")
    for item in bid_source.find(projection=["_id"]):
        ids.append(item.get("_id"))
    logger.info("collect all _ids end")
    count = skip_count

    # cursor = bid_source.find(batch_size=50)
    # for item in cursor:
    for i in range(skip_count, total_count):
        item = bid_source.find_one({"_id": ids[i]})

        count += 1
        if count <= skip_count:
            logger.info("{0}/{1}: SKIP COUNT".format(count, total_count))
            continue

        summary = item.get("summary")
        content = item.get("source", {}).get("content")

        result_item = parse.newBidItm()
        result_item["url"] = item.get("url")
        result_item["title"] = item.get("title")
        result_item["region"] = item.get("region")
        result_item["purchaser"] = item.get("purchaser")
        result_item["purchase_agent"] = item.get("purchaseAgent")
        result_item["purchase_category"] = item.get("purchaseCategory")
        result_item["published_ts"] = item.get("time")
        result_item["announced_ts"] = item.get("announced_ts")
        result_item["winning_ts"] = item.get("winning_ts")
        result_item["announce_type"] = item.get("bidType")
        # result_item["amount"] = item.get("amount")
        # result_item["unit"] = item.get("unit")
        # result_item["currency"] = item.get("currency")

        if result_item["published_ts"]:
            if re.match("\d+\.\d+\.\d+ \d+:\d+:\d+$", result_item["published_ts"]):
                time = datetime.datetime.strptime((result_item["published_ts"]), "%Y.%m.%d %H:%M:%S")
            elif re.match("\d+\.\d+\.\d+$", result_item["published_ts"]):
                time = datetime.datetime.strptime((result_item["published_ts"]), "%Y.%m.%d")
            else:
                time = datetime.datetime(2015, 10, 10)
            if time > datetime.datetime(2015, 10, 10):
                logger.info("{0}/{1}: SKIP TIME {2}".format(count, total_count, time))
                continue

        summary_res = {}
        if summary:
            summary_res = analysis_bid_summary(summary)
        result_item.update(summary_res)

        content_res = {"bid_time": "", "bid_result": []}
        if content:
            content_res = analysis_bid_announce(content, result_item)
        result_item["analysis_result"] = content_res

        try_time = 0
        while try_time < 3:
            try:
                session.post(config.TORNADO_SERVICE_URL, data={"announce_data": json.dumps(result_item)},
                             timeout=TIMEOUT)
                break
            except Exception, e:
                logger.info(e)
                try_time += 1

        if try_time < 3:
            logger.info("{0}/{1}: SUCCESS".format(count, total_count))
        else:
            logger.info("{0}/{1}: FAIL".format(count, total_count))

    # cursor.close()
    mongo_util.conn.close()
    session.close()


if __name__ == "__main__":
    main()
