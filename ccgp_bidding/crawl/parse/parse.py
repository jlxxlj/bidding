#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import math
import re
import datetime
from bs4 import BeautifulSoup
from scpy.logger import get_logger

import util
import find_all_info
import html_analysis
import html_preprocess

reload(sys)
sys.setdefaultencoding('utf-8')
logger = get_logger(__file__)


def newBidItm():
    return {
        'url': '',
        'title': '',
        'published_ts': '',
        'region': '',
        'purchase_agent': '',
        'purchaser': '',
        'purchase_category': '',
        'announce_type': ''
    }


def parse_page_num(html):
    """
    解析页数
    """
    soup = BeautifulSoup(html, 'lxml')
    announce_num = soup.find('span', style='color:#c00000')
    announce_num = int(announce_num.get_text()) if announce_num else 0
    max_page = int(math.ceil(announce_num / 20.0))
    return max_page


def parse_list_page(html, sign):
    soup = BeautifulSoup(html, 'html5lib')
    tmpBidList = soup.find('ul', attrs={'class': 'vT-srch-result-list-bid'})
    bidList = tmpBidList.findAll('li') if tmpBidList else []
    bidInfoList = []
    baseUrl = 'http://search.ccgp.gov.cn/'

    for bidItm in bidList:
        tmpBidInfo = newBidItm()
        tmpUrl = bidItm.find('a').get('href')

        if sign == 'old':
            tmpUrl = baseUrl + tmpUrl

        tmpBidInfo['url'] = tmpUrl
        tmpBidInfo['title'] = bidItm.find('a').get_text()
        spanText = bidItm.find('span').get_text().strip()
        # spanTextList = spanText.split('|')
        spanTextList = re.split(u"\||\n", spanText)
        spanTextList = [x for x in spanTextList if len(x.strip()) > 0]
        tmpBidInfo['published_ts'] = spanTextList[0].strip() if len(spanTextList) > 0 else ''
        tmpBidInfo['purchaser'] = spanTextList[1].strip().replace(u'采购人：', '') if len(spanTextList) > 1 else ''
        tmpBidInfo['purchase_agent'] = spanTextList[2].strip().replace(u'代理机构：', '') if len(spanTextList) > 2 else ''
        tmpBidInfo['announce_type'] = spanTextList[3].strip() if len(spanTextList) > 3 else ''
        tmpBidInfo['region'] = spanTextList[4].strip() if len(spanTextList) > 4 else ''
        announce_type = util.get_bid_type_by_title(tmpBidInfo.get("title"))
        if announce_type:
            tmpBidInfo['announce_type'] = announce_type

        if sign == 'old':
            tmpBidInfo['purchase_category'] = ''
        else:
            tmpBidInfo['purchase_category'] = spanTextList[5].strip() if len(spanTextList) > 5 else ''
        bidInfoList.append(tmpBidInfo)
    return bidInfoList


def parse_detail(html, item):
    """
    解析整个文本
    :param html:
    :param item:
    :return:
    """
    soup = BeautifulSoup(html, 'lxml')
    main_content = soup.find('div', class_="vT_detail_main")
    if not main_content:
        main_content = BeautifulSoup('', 'lxml')
    summary_table = main_content.find('div', class_='table')
    summary_res = {}
    if summary_table:
        summary_res = analysis_bid_summary(summary_table.prettify())
    item.update(summary_res)

    tmp_content = main_content.find('div', class_='vT_detail_content')
    content_res = {"bid_time": "", "bid_result": []}
    if tmp_content:
        content_res = analysis_bid_announce(tmp_content.prettify(), item)
    item["analysis_result"] = content_res


def analysis_bid_summary(html):
    """
    解析summary中的字段：招标公告日期、公告时间、中标日期、总中标金额、单位、货币
    :param html:
    :return:
    """
    res, summary = {}, {}

    summaryTable = BeautifulSoup(html, 'lxml')
    trLst = summaryTable.findAll('tr')
    for trItm in trLst:
        tdLst = trItm.findAll('td')
        if len(tdLst) == 1:
            continue
        for k in range(len(tdLst) / 2):
            tmpKey = tdLst[2 * k].get_text().strip()
            tmpValue = tdLst[2 * k + 1].get_text().strip()
            summary[tmpKey] = tmpValue

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


# 针对政府招投标网页被封，采取分别爬取中央和地方的中标/成交公告
def parse_announce_list(html, url):
    bs = html_preprocess.build_beautifulsoup(html)
    lst = bs.find("div", attrs={"class": "main_list"}).find_all("li")
    announce_type = bs.find("div", attrs={"class": "main_list"}).find("h2").get_text().strip()

    base_url = "/".join(list(url.split("/")[:-1]) + [""])
    items = []
    for it in lst:
        item = newBidItm()
        item["announce_type"] = announce_type
        item["url"] = base_url + it.find("a")["href"][2:]
        item["title"] = it.find("a")["title"]
        info = it.find_all("span")
        item["published_ts"] = info[0].get_text().strip()
        item["region"] = info[1].get_text().strip()
        item["purchaser"] = info[2].get_text().strip()
        items.append(item)

    next_page = bs.find("p", attrs={"class": "pager"}).find("a", attrs={"class": "next"})
    if next_page is not None:
        next_page = base_url + next_page["href"]
    else:
        page = re.findall("\d+", url)
        if len(page) == 1:
            current_page = int(page[0])
        elif len(page) == 0:
            current_page = 0
        else:
            current_page = 25
            logger.info("parse page error")
        if current_page < 24:
            next_page = base_url + "index_{0}.htm".format(current_page+1)

    return items, next_page

