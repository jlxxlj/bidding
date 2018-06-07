# coding=utf-8
# author="Jianghua Zhao"


"""
对招投标公告文档进行解析，提取其中有用信息
"""
import sys
import re
import json
import urllib
import copy

from scpy.logger import get_logger
from html_purify import purify_html

from announce_attributes import *
import html_convert_to_dict
import html_dict_analysis
from db.postgresql_sc import PostgresqlUtil
from db import aws_s3_sc

reload(sys)
sys.setdefaultencoding('utf-8')

database = PostgresqlUtil()
logger = get_logger(__file__)


def save_bidding_result(announce_data):
    """
    保存中标结果
    :param announce_data:
    :return:
    """
    announce_data = json.loads(announce_data)

    if len(announce_data) == 1:
        if not announce_data[0]["url"]:
            return
        database.delete(table="chong_qing_bidding_result", condition={"url": announce_data[0]["url"]})
    else:
        return

    for item in announce_data:

        if not item["url"]:
            continue
        if not item["project_name"]:
            del item["project_name"]
        if not item["region"]:
            del item["region"]
        if not item["published_ts"]:
            del item["published_ts"]
        if not item["purchaser_name"]:
            del item["purchaser_name"]
        if not item["purchaser_contact_phone"]:
            del item["purchaser_contact_phone"]
        if not item["agent_name"]:
            del item["agent_name"]
        if not item["agent_contact_phone"]:
            del item["agent_contact_phone"]
        if not item["amount"]:
            del item["amount"]
        if not item["unit"]:
            del item["unit"]
        if not item["currency"]:
            del item["currency"]
        if not item["winning_company"]:
            del item["winning_company"]

        database.insert(table="chong_qing_bidding_result", data=item)
        logger.info("Write an analysis result (%s)." % item.get("url"))


def announce_data_template():
    announce_data = dict(url="", project_name="", region="", published_ts="", amount=None, unit="", currency="",
                         winning_company="")
    return announce_data


def analysis(announce_item):
    """
    解析公告文本
    :param announce_item:
    :return:
    """
    content = announce_item.get("content")
    cont = purify_html(content)
    doc = html_convert_to_dict.analysis_html(cont)
    bidding_item = html_dict_analysis.analysis_announce_doc(doc, pre_info=announce_item, src_html=content)

    announce_data = announce_data_template()

    announce_data["url"] = bidding_item[URL]

    announce_data["project_name"] = bidding_item.get(PROJECT_NAME, "")
    if not announce_data["project_name"]:
        announce_data["project_name"] = bidding_item.get(TITLE, "")

    if bidding_item.get(REGION, ""):
        announce_data["region"] = bidding_item.get(REGION, "")
    else:
        announce_data["region"] = bidding_item.get(ORIGIN_REGION, "")

    announce_data["published_ts"] = bidding_item.get(PUBLISHED_TS, "")

    announce_data["purchaser_name"] = bidding_item.get(PURCHASER_NAME, "")

    announce_data["purchaser_contact_phone"] = bidding_item.get(PURCHASER_CONTACT_PHONE, "")

    announce_data["agent_name"] = bidding_item.get(AGENT_NAME, "")

    announce_data["agent_contact_phone"] = bidding_item.get(AGENT_CONTACT_PHONE, "")

    winners = []
    segments = bidding_item.get(SEGMENTS)
    for seg in segments:

        win = None
        winner = seg.get(WINNER)
        if winner:
            win = {"winning_company": winner.get(WINNING_COMPANY_NAME)}
            money = winner.get(WINNING_MONEY)
            if money:
                win["amount"] = money.get(MONEY_AMOUNT)
                win["unit"] = money.get(MONEY_UNIT)
                win["currency"] = money.get(MONEY_CURRENCY)
        else:
            candidates = seg.get(CANDIDATES)
            if len(candidates) > 0:
                winner = candidates[0]
                if winner.get(CANDIDATE_RANK) and winner.get(CANDIDATE_RANK) != 1:
                    for i in range(1, len(candidates)):
                        if candidates[i].get(CANDIDATE_RANK) == 1:
                            winner = candidates[i]
                            break
                win = {"winning_company": winner.get(CANDIDATE_COMPANY_NAME)}
                money = winner.get(CANDIDATE_MONEY)
                if money:
                    win["amount"] = money.get(MONEY_AMOUNT)
                    win["unit"] = money.get(MONEY_UNIT)
                    win["currency"] = money.get(MONEY_CURRENCY)
        # 去掉重复的,没有意义的结果
        if win:
            sig = True
            for i, win_ in enumerate(winners):
                if win_.get("winning_company") == win.get("winning_company"):
                    if win_.get("amount") is None and win.get("amount"):
                        winners[i] = win
                        sig = False
                    elif win_.get("amount") and win.get("amount") is None:
                        sig = False
                    elif win_.get("amount") == win.get("amount"):
                        sig = False
            if sig:
                winners.append(win)

    res = []
    for i, win in enumerate(winners):
        item = copy.deepcopy(announce_data)
        item.update(win)
        res.append(item)

        print "company:{0}, currency:{1}, amount:{2}, unit:{3}".format(
            win.get("winning_company"),
            win.get("currency"),
            win.get("amount"),
            win.get("unit"))

    return res


# 定时从s3中读取最新的数据分析并存库
def main():
    """
    公告解析算法主循环
    :return:
    """
    s3util = aws_s3_sc.S3Util()

    s3_client = aws_s3_sc.get_aws_client("s3")

    paginator = s3_client.get_paginator('list_objects')
    response_iterator = paginator.paginate(
        Bucket='bidding',
        Prefix='source/chong_qing/www.cqggzy.com',
    )

    for page in response_iterator:
        for item in page["Contents"]:
            object_key = item["Key"]

            # 验证object_key
            if "www.cqgp.gov.cn" in object_key or "www.cqzb.gov.cn" in object_key:
                continue

            # 从s3上读数据
            obj = s3util.select(table="bidding", condition={}, file_name=object_key)
            s3_data = json.loads(obj["Body"].read())
            if s3_data.get(PROJECT_TYPE) != u"工程建设":
                continue
            print "\n", object_key
            # try:
            # 分析数据
            announce_data = analysis(s3_data)
            # 存库
            save_bidding_result(json.dumps(announce_data))


def test():
    from urllib import urlencode
    key = "http://www.cqggzy.com/xxhz/014001/014001004/20170104/78285290-98cc-405f-80af-ec84fde0db69.html"
    s3_data_key = "source/chong_qing/www.cqggzy.com/2017/01/04/" + urlencode({"url": key})[4:] + ".json"

    s3util = aws_s3_sc.S3Util()
    obj = s3util.select(table="bidding", condition={}, file_name=s3_data_key)
    s3_data = json.loads(obj["Body"].read())
    announce_data = analysis(s3_data)
    save_bidding_result(json.dumps(announce_data))
    print announce_data


def analysis_announce_of_website(website):
    from announce_analysis_result_save import announce_analysis_result_save
    from announce_analysis import analysis

    s3util = aws_s3_sc.S3Util()
    s3_client = aws_s3_sc.get_aws_client("s3")
    paginator = s3_client.get_paginator('list_objects')
    response_iterator = paginator.paginate(
        Bucket='bidding',
        Prefix='source/chong_qing/' + website,
    )

    for page in response_iterator:
        for item in page.get("Contents", []):
            object_key = item["Key"]

            # 从s3上读数据
            logger.info("announce s3 key: " + object_key)
            try:
                obj = s3util.select(table="bidding", condition={}, file_name=object_key)
                s3_data = json.loads(obj["Body"].read())
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                logger.exception(e)
                continue

            # 分析数据
            try:
                announce_data = analysis(s3_data)
            except Exception as e:
                logger.exception(e)
                new_name = "parse_error/" + urllib.urlencode({"name": object_key})[5:]
                s3util.insert(table="bidding", data=s3_data, file_name=new_name)
                continue
            # 存库
            content_source = "s3:bidding:" + object_key
            announce_analysis_result_save(announce_data, content_source)


if __name__ == "__main__":
    # main()
    # test()
    analysis_announce_of_website("www.cqggzy.com")
