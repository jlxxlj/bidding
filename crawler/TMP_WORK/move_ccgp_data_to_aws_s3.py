# coding=utf-8
# author="Jianghua Zhao"

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import content_saver
from pymongo import MongoClient
import copy
import time
import datetime
from scpy.date_extractor import extract_first_date

import config.config as cfg
from util import *
from parser_helper import obtain_element_info

time_print = []


def extract_first_date_no_exception(text, is_str):
    try:
        return extract_first_date(text, is_str)
    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        return ""


def time_now(msg=""):
    if len(time_print) <= 0:
        time_print.append(time.time())
        print "DateTime(%s): %s" % (datetime.datetime.now(), msg)
    else:
        t = time.time()
        print "DateTime(%s) [%.6f]: %s" % (datetime.datetime.now(), round(t - time_print[0], 6), msg)
        time_print[0] = t


def parser_summary(summary, info):
    summary = build_beautiful_soup(summary)
    if summary:
        summary = summary.find("table")
    if summary:
        tds = summary.find_all("td")
        tds = tds[1:19] + tds[20:36]
        summary = {}
        for i in range(0, len(tds)-1, 2):
            summary[tds[i].get_text().strip()] = tds[i + 1].get_text().strip()

        if u"采购项目名称" in summary and summary[u"采购项目名称"] != u"详见公告正文":
            info[PROJECT_NAME] = summary[u"采购项目名称"]
        if u"品目" in summary and summary[u"品目"] != u"详见公告正文":
            info[PURCHASE_CATEGORY] = summary[u"品目"]
        if u"本项目招标公告日期" in summary and summary[u"本项目招标公告日期"] != u"详见公告正文":
            info[ANNOUNCED_TS] = extract_first_date_no_exception(summary[u"本项目招标公告日期"], is_str=True)
        if u"项目联系人" in summary and summary[u"项目联系人"] != u"详见公告正文":
            info[PROJECT_CONTACT_NAME] = summary[u"项目联系人"]
        if u"项目联系电话" in summary and summary[u"项目联系电话"] != u"详见公告正文":
            info[PROJECT_CONTACT_PHONE] = summary[u"项目联系电话"]
        if u"成交日期" in summary and summary[u"成交日期"] != u"详见公告正文":
            info[DEAL_TS] = extract_first_date_no_exception(summary[u"成交日期"], is_str=True)
        if u"中标日期" in summary and summary[u"中标日期"] != u"详见公告正文":
            info[WINNING_TS] = extract_first_date_no_exception(summary[u"中标日期"], is_str=True)
        if u"谈判小组、询价小组成员、磋商小组成员名单及单一来源采购人员名单" in summary and summary[u"谈判小组、询价小组成员、磋商小组成员名单及单一来源采购人员名单"] != u"详见公告正文":
            info[EXPERT_NAMES] = summary[u"谈判小组、询价小组成员、磋商小组成员名单及单一来源采购人员名单"]
        if u"评审专家名单" in summary and summary[u"评审专家名单"] != u"详见公告正文":
            info[EXPERT_NAMES] = summary[u"评审专家名单"]
        if u"总成交金额" in summary and summary[u"总成交金额"] != u"详见公告正文":
            money = obtain_element_info.obtain_money(summary[u"总成交金额"])
            if len(money) > 0:
                info[TOTAl_WINNING_MONEY] = obtain_element_info.regulate_money(money[0])
        if u"总中标金额" in summary and summary[u"总中标金额"] != u"详见公告正文":
            money = obtain_element_info.obtain_money(summary[u"总中标金额"])
            if len(money) > 0:
                info[TOTAl_WINNING_MONEY] = obtain_element_info.regulate_money(money[0])
        if u"采购单位" in summary and summary[u"采购单位"] != u"详见公告正文":
            info[PURCHASER_NAME] = summary[u"采购单位"]
        if u"采购单位地址" in summary and summary[u"采购单位地址"] != u"详见公告正文":
            info[PURCHASER_ADDRESS] = summary[u"采购单位地址"]
        if u"采购单位联系方式" in summary and summary[u"采购单位联系方式"] != u"详见公告正文":
            t = re.findall(u"[\u4e00-\u9fa5]+", summary[u"采购单位联系方式"])
            if len(t) > 0:
                info[PURCHASER_CONTACT_NAME] = t[0]
            t = obtain_element_info.obtain_phone_number(summary[u"采购单位联系方式"])
            if len(t) > 0:
                info[PURCHASER_CONTACT_PHONE] = t[0]
        if u"代理机构名称" in summary and summary[u"代理机构名称"] != u"详见公告正文":
            info[AGENT_NAME] = summary[u"代理机构名称"]
        if u"代理机构地址" in summary and summary[u"代理机构地址"] != u"详见公告正文":
            info[AGENT_ADDRESS] = summary[u"代理机构地址"]
        if u"代理机构联系方式" in summary and summary[u"代理机构联系方式"] != u"详见公告正文":
            t = re.findall(u"[\u4e00-\u9fa5]+", summary[u"代理机构联系方式"])
            if len(t) > 0:
                info[PURCHASER_CONTACT_NAME] = t[0]
            t = obtain_element_info.obtain_phone_number(summary[u"代理机构联系方式"])
            if len(t) > 0:
                info[AGENT_CONTACT_PHONE] = t[0]

    return info


def move_ccgp_data_to_aws_s3():
    mongo_client = MongoClient(host=cfg.MONGO_HOST, port=cfg.MONGO_PORT)
    db = mongo_client[cfg.MONGO_DB_NAME]
    bid_announce = db["bid_announce"]
    deal_announce = db["deal_announce"]
    # merged_announce = db["merged_announce"]

    saver = content_saver.ContentS3Saver()

    temp = {
        ORIGIN_REGION: u"全国",
        ANNOUNCE_TYPE: u"中标公告",
        PROJECT_TYPE: u"政府采购",
        WEBSITE: u"中国政府采购网",
        NOTE: u"中国政府采购网-中标公告"
    }

    time_now("start moving data")
    # for col, name in [(bid_announce, "bid_announce"), (deal_announce, "deal_announce")]:
    for col, name in [(deal_announce, "deal_announce")]:
        count, skip, stop = 0, 0, None

        # time_now("start")
        for it in col.find():
            count += 1
            if count <= skip:
                continue
            if stop and count > stop:
                break

            # time_now("loop start")

            item = copy.deepcopy(temp)
            if "url" not in it or "title" not in it or "time" not in it or "region" not in it:
                continue
            if "cjgg" in it['url']:
                item[ANNOUNCE_TYPE] = u"成交公告"

            item[URL] = it['url']
            item[TITLE] = it['title']
            item[PUBLISHED_TS] = it['time']
            item[REGION] = it.get("region", "")
            source = it.get("source", {})
            item[CONTENT] = source.get("content", "<div></div>")
            try:
                item = parser_summary("<div>%s</div>" % source.get("summary", ""), item)
            except:
                pass
            # time_now("parser summary")

            saver.save(item)
            # time_now("save result")
            if count % 100 == 0:
                time_now("%s::%8d items has been moved (%s)" % (name, count, it.get("url", "")))

        time_now("%s::%8d items has been moved" % (name, count))

    time_now("move_ccgp_data_to_aws_s3 done!")


if __name__ == "__main__":
    move_ccgp_data_to_aws_s3()
