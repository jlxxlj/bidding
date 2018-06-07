# coding=utf-8
# author="Jianghua Zhao"

import copy
import json
import math
import time
import datetime
from lxml import etree
import sys

from scpy import date_extractor

import parser_helper
from parser_helper import obtain_element_info
from parser_helper.html_preprocess import html_purify
from util import *

reload(sys)
sys.setrecursionlimit(10000)

PRE_PURIFY_CONTENT = False

__url_parser_table = []


def __uniform_html_code(html):
    try:
        if re.search('<meta.*?charset\=["]?(?:gb2312|gbk).*?>', html.lower()):
            html = html.decode(encoding="gbk")
        elif re.search('<meta.*?charset\=["]?utf-8.*?>', html.lower()):
            html = html.decode(encoding="utf-8")
    except:
        pass
    return html


def get_matched_parser(url):
    for ct in __url_parser_table:
        if re.match(ct[0], url):
            return ct
    return None


def add_url(url):
    def decorator(function):
        def fun(html, pre_information):
            html = __uniform_html_code(html)
            return function(html, pre_information)

        __url_parser_table.append((url, fun))
        return fun

    return decorator


def url_filter(url, *args):
    re_keyword = "\\.-?()"
    for item in re_keyword:
        url = url.replace(item, "\\" + item)
    url = url % args
    return url


def next_pages(pre_info, func, current_page, total_page):
    next_page_info_list = []

    if pre_info.get(GENERATED_PAGE):
        current_page = max(current_page, pre_info.get(GENERATED_PAGE))

    while current_page < total_page:
        next_page_info = copy.deepcopy(pre_info)
        func(next_page_info, current_page + 1)
        if pre_info.get(GENERATE_ALL_PAGE):  # 判断是否直接生成后面所有目录页地址
            next_page_info[GENERATED_PAGE] = total_page
            next_page_info_list.append(next_page_info)
            current_page += 1
        else:
            next_page_info_list.append(next_page_info)
            break

    return next_page_info_list


def extract_first_date(text, is_str=True):
    try:
        return date_extractor.extract_first_date(text, is_str)
    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        print e.message
    return ""


# *********招投标爬虫信息抽取配置*********招投标爬虫信息抽取配置********* #
# *********招投标爬虫信息抽取配置*********招投标爬虫信息抽取配置********* #
# *********招投标爬虫信息抽取配置*********招投标爬虫信息抽取配置********* #

# ================START================ #
# ================台  湾================ #

# ================台  湾================ #
# =================END================= #


# ================START================ #
# ================澳  门================ #

# ================澳  门================ #
# =================END================= #


# ================START================ #
# ================香  港================ #

# ================香  港================ #
# =================END================= #


# ================START================ #
# ================宁  夏================ #

@add_url(url_filter("http://www.nxzfcg.gov.cn/ningxia/services/BulletinWebServer/getInfoListInAbout"))
def nx_ggzyjyzx_ml(html, pre_information):
    links, contents = [], []

    # 找到所有列表项目地址
    host = "http://www.nxzfcg.gov.cn/ningxia/WebbuilderMIS/RedirectPage/RedirectPage.jspx?infoid={0}&categorynum={1}&locationurl=http://www.nxggzyjy.org/ningxiaweb"
    data = json.loads(html, strict=False)
    lst = json.loads(data["return"], strict=False)
    lst = lst.get("Table", [])
    for item in lst:
        info = copy.deepcopy(pre_information)
        info[URL] = host.format(item["infoid"], item["categorynum"])
        reg = re.findall(u"^\[[\u4e00-\u9fa5]+\]", item["title"])
        if len(reg) > 0:
            info[REGION] = info[ORIGIN_REGION] + ">>" + reg[0].strip(u"[]")
        info[TITLE] = re.sub(u"^\[[\u4e00-\u9fa5]+\]", u"", item["title"])
        links.append(info)

    # 找到所有目录后面页地址
    current_page = re.findall("(?<=pageIndex\=)\d+", pre_information[URL])
    if len(current_page) == 0:
        current_page = 1
    else:
        current_page = int(current_page[0])

    total_page = current_page
    if len(lst) > 0:
        total_page = current_page + 1

    def next_page_func(info, next_page):
        info[URL] = re.sub("pageIndex\=\d+", "pageIndex=%s" % next_page, info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.nxggzyjy.org/ningxiaweb/002"))
@add_url(url_filter("http://www.nxzfcg.gov.cn/ningxia/WebbuilderMIS/RedirectPage/RedirectPage.jspx"))
def nx_ggzyjyzx_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", id="mainContent")
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)
    ps = bs.find("div", attrs={"class": "info-source"})
    info[PUBLISHED_TS] = extract_first_date(ps.get_text())
    contents.append(info)

    return links, contents


# ================宁  夏================ #
# =================END================= #


# ================START================ #
# ================广  西================ #
# 广西壮族自治区政府采购网
# 广西-省级-成交公告
# 广西-省级-成交公告-目录
@add_url(url_filter("http://www.gxzfcg.gov.cn/CmsNewsController/getCmsNewsList/channelCode-shengji_zbgg"))
@add_url(url_filter("http://www.gxzfcg.gov.cn/CmsNewsController/getCmsNewsList/channelCode-shengji_cjgg"))
@add_url(url_filter("http://www.gxzfcg.gov.cn/CmsNewsController/getCmsNewsList/channelCode-sxjcg_zbgg"))
@add_url(url_filter("http://www.gxzfcg.gov.cn/CmsNewsController/getCmsNewsList/channelCode-sxjcg_cjgg"))
def gx_sj_cj_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.gxzfcg.gov.cn"
    bs = build_beautiful_soup(html)
    lst = bs.find(attrs={"class": "column infoLink noBox unitWidth_x6"}).find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        a = item.find("a")
        info[TITLE] = a["title"]
        info[URL] = host + a["href"]
        info[PUBLISHED_TS] = extract_first_date(item.find(attrs={"class": "date"}).get_text(), is_str=True)
        region = item.find(attrs={"class": "emLevel_0"})
        if region is not None:
            if REGION in info:
                info[REGION] = info[REGION] + ">>" + region.get_text().strip("[]")
            else:
                info[REGION] = info[ORIGIN_REGION] + ">>" + region.get_text().strip("[]")
        links.append(info)

    # 找到所有目录后面页地址
    pager = bs.find(id="QuotaList_paginate")
    pager = pager.find("span").get_text()
    current_page, total_page = re.findall("\d+", pager)
    current_page = int(current_page)
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    total_page = int(total_page)

    while current_page < total_page:
        next_page_info = copy.deepcopy(pre_information)
        next_page_info[URL] = "_".join(pre_information["url"].split("_")[:-1] + ["%s.html" % (int(current_page) + 1)])
        if pre_information.get(GENERATE_ALL_PAGE):  # 判断是否直接生成后面所有目录页地址
            next_page_info[GENERATED_PAGE] = total_page
            links.append(next_page_info)
            current_page += 1
        else:
            links.append(next_page_info)
            break

    return links, contents


# 广西-省级-成交公告-内容
@add_url("http://www.gxzfcg.gov.cn/view/staticpags/shengji_zbgg/[0-9a-z]+")
@add_url("http://www.gxzfcg.gov.cn/view/staticpags/shengji_cjgg/[0-9a-z]+")
@add_url("http://www.gxzfcg.gov.cn/view/staticpags/sxjcg_zbgg/[0-9a-z]+")
@add_url("http://www.gxzfcg.gov.cn/view/staticpags/sxjcg_cjgg/[0-9a-z]+")
def gx_sj_cj_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find(attrs={"class": "frameReport"})
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)
    contents.append(info)

    return links, contents


# 广西壮族自治区政府采购中心
# 广西-目录
@add_url("http://www.gxgp.gov.cn/zbgkzb/index")
@add_url("http://www.gxgp.gov.cn/zbjz/index")
@add_url("http://www.gxgp.gov.cn/zbdyly/index")
@add_url("http://www.gxgp.gov.cn/zbxjcg/index")
def gx_gkzb_ml(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    lst = bs.find("div", attrs={"class": "list pic_news"}).find_all("div", attrs={"class": "c1-bline"})
    for item in lst:
        info = copy.deepcopy(pre_information)
        info[URL] = item.find("a")["href"]
        info[TITLE] = item.find("a")["title"]
        info[PUBLISHED_TS] = extract_first_date(item.find(attrs={"class": "f-right"}).get_text(), is_str=True)
        links.append(info)

    # 找到所有目录后面页地址
    pager = bs.find("div", attrs={"class": "pg-3"})
    current_page = re.findall("\d+", pre_information[URL])
    if len(current_page) == 0:
        current_page = 1
    else:
        current_page = int(current_page[0])
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    total_page = pager.find("span", attrs={"class": "total"}).get_text().strip()
    total_page = int(re.findall("\d+", total_page)[0])
    while current_page < total_page:
        next_page_info = copy.deepcopy(pre_information)
        next_page_info[URL] = re.sub(u"index(?:_\d+|)", u"index_%s" % (current_page + 1), pre_information[URL])
        if pre_information.get(GENERATE_ALL_PAGE):  # 判断是否直接生成后面所有目录页地址
            next_page_info[GENERATED_PAGE] = total_page
            links.append(next_page_info)
            current_page += 1
        else:
            links.append(next_page_info)
            break

    return links, contents


# 广西-内容
@add_url("http://www.gxgp.gov.cn/zbgkzb/[0-9]+")
@add_url("http://www.gxgp.gov.cn/zbjz/[0-9]+")
@add_url("http://www.gxgp.gov.cn/zbdyly/[0-9]+")
@add_url("http://www.gxgp.gov.cn/zbxjcg/[0-9]+")
def gx_gkzb_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", attrs={"class": "pbox"})
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(str(content))
    info[CONTENT] = str(content)
    contents.append(info)

    return links, contents


# ================广  西================ #
# =================END================= #


# ================START================ #
# ================西  藏================ #


# 西藏自治区招标投标网
@add_url(url_filter("http://www.xzzbtb.gov.cn/xz/publish-notice!preAwardNoticeView.do"))
def xz_zzqztbw_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.xzzbtb.gov.cn"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find("ul", attrs={"class": "x-consume_sqs-jr-top-content"}).find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        t = item.find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t.get_text().strip()
        t = item.find("span", attrs={"class": "jr-t-date"})
        info[PUBLISHED_TS] = extract_first_date(t.get_text(), is_str=True)
        links.append(info)

    # 找到所有目录后面页地址
    current_page = re.findall("\d+", pre_information[URL])
    if len(current_page) == 0:
        current_page = 1
    else:
        current_page = int(current_page[0])
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    pager = bs.find("div", attrs={"class": "pagination"})
    total_page = int(re.findall("\d+", pager.get_text())[2])

    while current_page < total_page:
        next_page_info = copy.deepcopy(pre_information)
        if "PAGE" in next_page_info[URL]:
            next_page_info[URL] = re.sub("PAGE\=\d+", "PAGE=%s" % (current_page + 1), next_page_info[URL])
        else:
            next_page_info[URL] += "?PAGE=%s" % (current_page + 1)
        if pre_information.get(GENERATE_ALL_PAGE):  # 判断是否直接生成后面所有目录页地址
            next_page_info[GENERATED_PAGE] = total_page
            links.append(next_page_info)
            current_page += 1
        else:
            links.append(next_page_info)
            break

    return links, contents


@add_url(url_filter("http://www.xzzbtb.gov.cn/xz/publish-notice!view.do"))
def xz_zzqztbw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    iframe = bs.find("iframe", id="consume_sqs")

    host = "http://www.xzzbtb.gov.cn/xz/"
    info = copy.deepcopy(pre_information)
    info[DATA_URL] = host + iframe["src"]

    links.append(info)

    return links, contents


@add_url(url_filter("http://www.xzzbtb.gov.cn/xz/pre-award-notice!preViewNotice.do"))
def xz_zzqztbw_dt(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", id="myPrintArea")

    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================西  藏================ #
# =================END================= #


# ================START================ #
# ================新  疆================ #

# 新疆维吾尔自治区政府采购网
@add_url(url_filter("http://zfcg.xjcz.gov.cn/djl/cmsPublishAction.do?"))
def xj_zfcgw_ml(html, pre_information):
    links, contents = [], []

    host = "http://zfcg.xjcz.gov.cn"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find_all("div", attrs={"class": "left layout2_list_row2"})
    for item in lst:
        info = copy.deepcopy(pre_information)
        t = item.find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t.get_text().strip()
        t = item.find("div", attrs={"class": "right layout2_list_time"})
        info[PUBLISHED_TS] = extract_first_date(t.get_text(), is_str=True)
        links.append(info)

    # 找到所有目录后面页地址
    current_page = pre_information[PARAMS]["pagecount"]
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    pager = bs.find("div", attrs={"class": "left page_list_page"})
    total_page = pager.find_all("a")[-1]["onclick"]
    total_page = int(re.findall("\d+", total_page)[0])

    while current_page < total_page:
        next_page_info = copy.deepcopy(pre_information)
        next_page_info[PARAMS]["pagecount"] = current_page + 1
        if pre_information.get(GENERATE_ALL_PAGE):  # 判断是否直接生成后面所有目录页地址
            next_page_info[GENERATED_PAGE] = total_page
            links.append(next_page_info)
            current_page += 1
        else:
            links.append(next_page_info)
            break

    return links, contents


@add_url(url_filter("http://zfcg.xjcz.gov.cn/mos/cms/html/"))
def xj_zfcgw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", attrs={"class": "left article_con"})

    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================新  疆================ #
# =================END================= #


# ================START================ #
# ================内蒙古================ #
# 内蒙古自治区公共资源交易网
@add_url(url_filter("http://www.nmgzfcg.gov.cn/jyxx/jsgcZbjggs%s", "$"))
@add_url(url_filter("http://www.nmgzfcg.gov.cn/jyxx/zfcg/zbjggs%s", "$"))
def nmg_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.nmgzfcg.gov.cn"
    bs = build_beautiful_soup(html)
    if pre_information.get(METHOD) is not POST:
        regs = bs.find("div", attrs={"class": "hubs"}).find_all("a")
        industries_type = bs.find("input", attrs={"id": "industriesTypeCode"})["value"]
        scroll_value = bs.find("input", attrs={"id": "scrollValue"})["value"]
        for rg in regs:
            rg_code = rg["id"]
            rg_text = rg.get_text().strip()

            param = {"currentPage": 1,
                     "area:": rg_code,
                     "industriesTypeCode": industries_type,
                     "scrollValue": scroll_value,
                     "bulletinName": "",
                     "secondArea": ""}

            info = copy.deepcopy(pre_information)
            info[METHOD] = POST
            info[PARAMS] = param
            info[REGION] = info[ORIGIN_REGION] + ">>" + rg_text
            print json.dumps(info, indent=4).decode("unicode-escape")
            links.append(info)
        return links, contents

    lst = bs.find("table", id="data_tab").find_all("tr")
    if len(lst) > 0:
        lst = lst[1:]
    for item in lst:
        info = copy.deepcopy(pre_information)
        tds = item.find_all("td")
        t = tds[1].find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t["title"]
        info[PUBLISHED_TS] = extract_first_date(tds[2].get_text(), is_str=True)
        info[METHOD] = GET
        links.append(info)

    current_page = pre_information[PARAMS]["currentPage"]

    total_page = 0
    pager = bs.find("div", attrs={"class": "mmggxlh"})
    if pager:
        pages = re.findall("\d+", unicode(pager))
        if len(pages) > 0:
            total_page = int(pages[-1])

    def next_page_func(info, next_page):
        info[PARAMS]["currentPage"] = next_page

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.nmgzfcg.gov.cn/jyxx/jsgcZbjggsDetail?guid="))
@add_url(url_filter("http://www.nmgzfcg.gov.cn/jyxx/zfcg/zbjggsDetail?guid="))
def nmg_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", attrs={"class": "detail_contect"})
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)
    contents.append(info)

    return links, contents


# 内蒙古自治区政府采购网
# 遍历发布时间
@add_url(url_filter("http://www.nmgp.gov.cn/procurement/pages/tender.jsp?type=2&pos=1"))
def nmg_zfcgw_seg(html, pre_information):
    links, contents = [], []

    host = "http://www.nmgp.gov.cn/procurement/pages/tender.jsp?type=2&pos=1"
    st_date = datetime.date(year=2013, month=12, day=1)
    select_date = datetime.datetime.now().date()
    one_day = datetime.timedelta(days=1)
    while select_date > st_date:
        pubdates = select_date.strftime("%Y-%m-%d")
        pubdatee = (select_date + one_day).strftime("%Y-%m-%d")
        select_date -= one_day
        info = copy.deepcopy(pre_information)

        info[URL] = host + ("&pubdates=%s&pubdatee=%s" % (pubdates, pubdatee))
        info[PUBLISHED_TS] = pubdates
        links.append(info)

    return links, contents


@add_url(url_filter("http://www.nmgp.gov.cn/procurement/pages/tender.jsp?type=2&pos=%s&pubdates=", "\d+"))
def nmg_zfcgw_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.nmgp.gov.cn"
    bs = build_beautiful_soup(html)
    lst = bs.find("table", attrs={"class": "recordlist"}).find_all("tr")
    for item in lst:
        info = copy.deepcopy(pre_information)
        tds = item.find_all("td")
        t = tds[0].find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t["title"]
        t = tds[0].find("font")
        t = t.get_text().strip("[] \n").split("|")
        if len(t) == 2:
            info[REGION] = info[ORIGIN_REGION] + ">>" + t[0]
            info[PURCHASE_CATEGORY] = t[1]
        links.append(info)

    current_page = re.findall("(?<=pos\=)\d+", pre_information[URL])
    current_page = int(current_page[0])

    total_page = 0
    pager = bs.find("div", attrs={"class": "pagenumber"})
    if pager:
        pages = pager.find_all("a")
        if len(pages) > 1:
            total_page = int(pages[-2].get_text().strip())

    def next_page_func(info, next_page):
        info[URL] = re.sub("pos\=\d+", "pos=%s" % next_page, info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.nmgp.gov.cn/static"))
def nmg_zfcgw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", attrs={"id": "wrapper"})
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)
    contents.append(info)

    return links, contents


# ================内蒙古================ #
# =================END================= #


# ================START================ #
# ================海  南================ #
# 中国海南政府采购网-2016年6月6日后数据
@add_url(url_filter("http://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?%sbid_type=10", ".*"))
@add_url(url_filter("http://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?%sbid_type=11", ".*"))
def hn_zbgg_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.ccgp-hainan.gov.cn"
    bs = build_beautiful_soup(html)
    lst = bs.find("div", attrs={"class": "nei02_04_01"}).find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        t = item.find("em").find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t.get_text().strip()
        info[PUBLISHED_TS] = extract_first_date(item.find("i").get_text(), is_str=True)
        if REGION in info:
            info[REGION] = info.get(REGION) + ">>" + item.find("b").get_text().strip()
        else:
            info[REGION] = info.get(ORIGIN_REGION) + ">>" + item.find("b").get_text().strip()
        links.append(info)

    pager = bs.find("div", attrs={"class": "nei02_04_02"})
    current_page = re.findall("(?<=currentPage=)\d+", pre_information[URL])
    if len(current_page) == 0:
        current_page = 1
    else:
        current_page = int(current_page[0])
    total_page = pager.get_text().strip()
    total_page = int(re.findall("\d+", total_page)[0])
    while current_page < total_page:
        next_page_info = copy.deepcopy(pre_information)
        next_page_info[URL] = re.sub(u"\?(?:currentPage\=\d+&|)", u"?currentPage=%s&" % (current_page + 1),
                                     pre_information[URL])
        if pre_information.get(GENERATE_ALL_PAGE):  # 判断是否直接生成后面所有目录页地址
            next_page_info[GENERATED_PAGE] = total_page
            links.append(next_page_info)
            current_page += 1
        else:
            links.append(next_page_info)
            break

    return links, contents


@add_url(url_filter("http://www.ccgp-hainan.gov.cn/cgw/cgw_show_zbgg.jsp?id=%s", "[0-9]+"))
@add_url(url_filter("http://www.ccgp-hainan.gov.cn/cgw/cgw_show_cjgg.jsp?id=%s", "[0-9]+"))
def hn_zbgg_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    time_tag = bs.find("div", attrs={"class": "basic"})
    content = bs.find("div", attrs={"class": "content01"})
    info = copy.deepcopy(pre_information)
    info[PUBLISHED_TS] = extract_first_date(time_tag.get_text(), is_str=True)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)
    contents.append(info)

    return links, contents


# 中国海南政府采购网-2016年6月6日前历史数据
@add_url(url_filter("http://www.hainan.gov.cn/was5/search/rollnews.jsp"))
def hn_zfcgw_cjgg_ml(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    lst = bs.find("dl", attrs={"class": "ny_news_lb"}).find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        t = item.find("a")
        info[URL] = t["href"]
        info[TITLE] = t.get_text().strip()
        info[PUBLISHED_TS] = extract_first_date(item.find("span").get_text(), is_str=True)
        links.append(info)

    pager = bs.find("div", attrs={"id": "pager"})
    current_page = re.findall("(?<=page=)\d+", pre_information[URL])
    if len(current_page) == 0:
        current_page = 1
    else:
        current_page = int(current_page[0])
    total_page = pager.get_text().strip()
    total_page = int(re.findall("\d+", total_page)[-1])
    while current_page < total_page:
        next_page_info = copy.deepcopy(pre_information)
        next_page_info[URL] = re.sub(u"page=\d+", u"page=%s" % (current_page + 1), pre_information[URL])
        if pre_information.get(GENERATE_ALL_PAGE):  # 判断是否直接生成后面所有目录页地址
            next_page_info[GENERATED_PAGE] = total_page
            links.append(next_page_info)
            current_page += 1
        else:
            links.append(next_page_info)
            break

    return links, contents


@add_url(url_filter("http://www.wenchang.gov.cn"))
@add_url(url_filter("http://mof.hainan.gov.cn/czt/zwxx/zfcg/cjgg/"))
def hn_zfcgw_cjgg_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    time_tag = bs.find("div", attrs={"class": "info"})  # .find("div", attrs={"class": "showbody1"})
    content = bs.find("div", id="contentText")
    info = copy.deepcopy(pre_information)
    info[PUBLISHED_TS] = extract_first_date(time_tag.get_text(), is_str=True)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)
    contents.append(info)

    return links, contents


# ================海  南================ #
# =================END================= #


# ================START================ #
# ================广  东================ #

@add_url(url_filter("http://www.gdgpo.gov.cn/queryMoreInfoList"))
def gd_zbgg_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.gdgpo.gov.cn"
    bs = build_beautiful_soup(html)
    lst = bs.find("div", attrs={"class": "m_m_cont"}).find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        reg, link = item.find_all("a")
        info[URL] = host + link["href"]
        info[TITLE] = link["title"]
        if REGION in info:
            info[REGION] = info[REGION] + ">>" + reg.get_text().strip()
        else:
            info[REGION] = info[ORIGIN_REGION] + ">>" + reg.get_text().strip()
        info[PUBLISHED_TS] = extract_first_date(item.find("em").get_text(), is_str=True)
        links.append(info)

    pager = bs.find("div", attrs={"class": "m_m_c_page"})
    current_page = pre_information[PARAMS]["pageIndex"]
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    total_page = find_tag_with_text(pager, name="a", text=u"尾  页")["href"]
    total_page = int(re.findall("\d+", total_page)[0])
    while current_page < total_page:
        next_page_info = copy.deepcopy(pre_information)
        next_page_info[PARAMS]["pageIndex"] = current_page + 1
        if pre_information.get(GENERATE_ALL_PAGE):  # 判断是否直接生成后面所有目录页地址
            next_page_info[GENERATED_PAGE] = total_page
            links.append(next_page_info)
            current_page += 1
        else:
            links.append(next_page_info)
            break

    return links, contents


@add_url(url_filter("http://www.gdgpo.gov.cn/showNotice/id/"))
def gd_zbgg_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    summary = bs.find("div", attrs={"class": "zw_c_c_qx"})
    content = bs.find("div", attrs={"class": "zw_c_c_cont"})

    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    summary_items = summary.find_all("span")
    summary = {}
    for item in summary_items:
        kv = item.get_text().split(u"：")
        kv = [x.strip() for x in kv]
        if len(kv) == 2 and len(kv[0]) > 0 and len(kv[1]) > 0:
            summary[kv[0]] = kv[1]
    info[PUBLISHED_TS] = extract_first_date(summary.get(u"发布日期", ""), is_str=True)
    info[PURCHASE_CATEGORY] = summary.get(u"采购品目")
    info[AGENT_NAME] = summary.get(u"代理机构")
    info[PROJECT_CONTACT_NAME] = summary.get(u"项目负责人")
    info[AGENT_CONTACT_NAME] = summary.get(u"项目经办人")
    money = summary.get(u"中标金额")
    if money:
        money = re.sub("\s", "", money)
        money = obtain_element_info.obtain_money(money)
        if len(money) > 0:
            info[TOTAl_WINNING_MONEY] = obtain_element_info.regulate_money(money[0])

    for key in summary.keys():
        if key in [u"发布日期", u"采购品目", u"代理机构", u"项目负责人", u"项目经办人", u"中标金额"]:
            del summary[key]
    info[OTHERS] = summary

    contents.append(info)

    return links, contents


# 广东阳江公共资源交易中心
@add_url(url_filter("http://www.yjggzy.cn/Query/"))
def sh_ggzyjyzx_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.yjggzy.cn"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find("div", attrs={"class": "Rbox"}).find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        t = item.find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t["title"]
        t = item.find("span")
        info[PUBLISHED_TS] = extract_first_date(t.get_text())
        links.append(info)

    # 找到所有目录后面页地址
    current_page = int(re.findall("\d+", pre_information[URL])[-1])
    pager = bs.find("div", attrs={"class": "pagination"})
    total_page = current_page
    if u"末页" in pager.get_text():
        t = pager.find_all("a")[-1]
        total_page = int(re.findall("\d+", t["href"])[-1])

    def next_page_func(info, next_page):
        info[URL] = re.sub("page\=\d+", "page=%s" % next_page, info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.yjggzy.cn/Details"))
@add_url(url_filter("http://www.yjggzy.cn/JsgcTemplate"))
def sh_ggzyjyzx_nr(html, pre_information):
    links, contents = [], []

    # html = html_purify(html)
    bs = build_beautiful_soup(html)
    content = bs.find("dl", attrs={"class": "acticlecontent"})
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================广  东================ #
# =================END================= #


# ================START================ #
# ================云  南================ #
# 云南政府采购网
@add_url(url_filter("http://www.yngp.com/bulletin.do?method=moreListQuery"))
def yn_zfcg_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.yngp.com/bulletin_zz.do?method=showBulletin&bulletin_id="
    data = json.loads(html.decode("gbk"))
    lst = data.get("rows", [])
    for item in lst:
        info = copy.deepcopy(pre_information)
        info[METHOD] = GET
        if PARAMS in info:
            del info[PARAMS]
        info[URL] = host + item["bulletin_id"]
        info[TITLE] = item["bulletintitle"]
        info[REGION] = info[ORIGIN_REGION] + ">>" + item.get("codeName")
        info[PUBLISHED_TS] = extract_first_date(item.get("finishday", ""))
        links.append(info)

    current_page = pre_information[PARAMS]["current"]
    total_page = data.get("totlePageCount", current_page)

    def next_page_func(info, next_page):
        info[PARAMS]["current"] = next_page

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.yngp.com/bulletin_zz.do?method=showBulletin&bulletin_id="))
def yn_zfcg_nr(html, pre_information):
    links, contents = [], []

    # not implement
    bs = build_beautiful_soup(html)
    content = bs.find("table", attrs={"border": '0', "cellspacing": '0', "cellpadding": '10', "width": '100%'})
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)
    contents.append(info)

    return links, contents


# ================云  南================ #
# =================END================= #


# ================START================ #
# ================贵  州================ #

@add_url(url_filter("http://www.gzzbw.cn/searchCustom"))
def gz_ztbw_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.gzzbw.cn"
    bs = build_beautiful_soup(html)
    lst = bs.find("table", attrs={"class": "table textcenter"}).find_all("tr")[1:]
    for item in lst:
        info = copy.deepcopy(pre_information)
        tds = item.find_all("td")
        t = tds[0].find("a")
        info[URL] = t["href"].replace(u"http://220.197.198.65:80", host)
        info[TITLE] = t.get_text().strip()
        t = tds[1].get_text().strip()
        info[TOTAl_WINNING_MONEY] = 10000 * float(tds[1].get_text().strip())
        info[PUBLISHED_TS] = extract_first_date(tds[2].get_text())
        links.append(info)

    current_page = re.findall("(?<=searchCustom_)\d+", pre_information[URL])
    if len(current_page) == 0:
        current_page = 1
    else:
        current_page = int(current_page[0])
    pager = bs.find("div", attrs={"class": "new_table"})
    total_page = re.findall(u"\d+/(\d+)页", pager.get_text())
    total_page = int(total_page[0]) if total_page else 0

    def next_page_func(info, next_page):
        info[URL] = re.sub("searchCustom(?:_\d+|)", "searchCustom_%s" % next_page, info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.gzzbw.cn/zbgs/"))
def gz_ztbw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    title = bs.find("span", attrs={"id": "titleContent"})
    agent = bs.find("div", attrs={"class": "content-inf"})
    content = bs.find("div", attrs={"class": "content-txt"})

    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)
    t = re.findall(u"发布单位：([\u4e00-\u9fa5]+)", agent.get_text())
    if t:
        info[AGENT_NAME] = t[0]
    info[TITLE] = title.get_text().strip()

    contents.append(info)

    return links, contents


# ================贵  州================ #
# =================END================= #


# ================START================ #
# ================青  海================ #

# 青海省政府采购
@add_url(url_filter("http://www.ccgp-qinghai.gov.cn/jilin/zbxxController.form?declarationType=W&type=1&pageNo"))
@add_url(url_filter("http://www.ccgp-qinghai.gov.cn/jilin/zbxxController.form?declarationType=W&type=2&pageNo"))
def qh_zfcg_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.ccgp-qinghai.gov.cn"
    bs = build_beautiful_soup(html)
    lst = bs.find("div", attrs={"class": "m_list_3"}).find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        t = item.find("a")
        info[URL] = t["href"]
        info[DATA_URL] = host + "/" + t["href"].split("=")[-1]
        info[TITLE] = t["title"]
        info[PUBLISHED_TS] = extract_first_date(item.find("span").get_text(), is_str=True)
        links.append(info)

    pager = bs.find("div", attrs={"style": "width:747px; height: 80px;text-align: center; font-size: 14px;"})
    page = re.findall("\d+", pager.get_text())
    current_page = int(page[1])
    total_page = int(page[2])
    while current_page < total_page:
        next_page_info = copy.deepcopy(pre_information)
        next_page_info[URL] = re.sub("pageNo\=\d+", "pageNo=%s" % current_page, next_page_info[URL])
        if pre_information.get(GENERATE_ALL_PAGE):  # 判断是否直接生成后面所有目录页地址
            next_page_info[GENERATED_PAGE] = total_page
            links.append(next_page_info)
            current_page += 1
        else:
            links.append(next_page_info)
            break

    return links, contents


@add_url(url_filter("http://www.ccgp-qinghai.gov.cn/html"))
def qh_zfcg_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("body")
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================青  海================ #
# =================END================= #


# ================START================ #
# ================甘  肃================ #
@add_url(url_filter("http://www.gszfcg.gansu.gov.cn/web/doSearch.action"))
def gs_cfcg_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.gszfcg.gansu.gov.cn"
    bs = build_beautiful_soup(html)
    lst = bs.find("ul", attrs={"class": "Expand_SearchSLisi"}).find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        t = item.find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t.get_text().strip()
        t = item.find("span")
        its = parser_helper.util.split_text(u"\|", t.get_text())
        for it in its:
            kv = parser_helper.util.split_text(u"：", it)
            if len(kv) != 2:
                continue
            if kv[0] == u"开标时间":
                info[OPEN_BID_TS] = extract_first_date(kv[1])
            if kv[0] == u"发布时间":
                info[PUBLISHED_TS] = extract_first_date(kv[1])
            if kv[0] == u"采购人":
                info[PURCHASER_NAME] = kv[1]
            if kv[0] == u"代理机构":
                info[AGENT_NAME] = kv[1]
        t = item.find("strong")
        its = t.get_text().split("|")
        if len(its) == 3:
            info[ANNOUNCE_TYPE] = its[0].strip()
            info[REGION] = info[ORIGIN_REGION] + ">>" + its[1].strip()
            info[PURCHASE_CATEGORY] = its[2].strip()
        links.append(info)

    current_page = re.findall("(?<=start\=)\d+", pre_information[URL])
    if len(current_page) == 0:
        current_page = 1
    else:
        current_page = int(current_page[0]) / 20 + 1
    total_page = current_page
    if len(links) == 20:
        total_page = current_page + 1

    def next_page_func(info, next_page):
        if "limit=20" not in info[URL]:
            info[URL] += ("&limit=20&start={0}".format(20 * next_page - 20))
        else:
            info[URL] = re.sub("start\=\d+", "start=%s" % (20 * next_page - 20), info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.gszfcg.gansu.gov.cn/web/article/"))
def yn_zfcg_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    summary = bs.find("table")
    content = bs.find("div", attrs={"class": "conTxt"})
    content = "<div>%s %s</div>" % (str(summary), str(content))
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    tds = summary.find_all("td")[1:]
    summary = {}
    for i in range(len(tds) / 2):
        k = tds[2 * i].get_text().strip()
        v = tds[2 * i + 1].get_text().strip()
        if len(k) > 0 and len(v) > 0:
            summary[k] = v
    info[PURCHASER_NAME] = summary.get(u"采购人：")
    info[AGENT_NAME] = summary.get(u"代理机构：")
    if u"采购预算：(万元)" in summary:
        money = summary.get(u"采购预算：(万元)")
        if re.match("(\d+)(?:\.\d+)$", money):
            moneys = obtain_element_info.obtain_money(u"采购预算：(万元)" + money)
            if len(moneys) == 1:
                money = obtain_element_info.regulate_money(moneys[0])
            info[PROJECT_BUDGET] = money

    for key in summary.keys():
        if key in [u"采购人：", u"代理机构：", u"采购预算：(万元)"]:
            del summary[key]
    info[OTHERS] = summary

    contents.append(info)

    return links, contents


# ================甘  肃================ #
# =================END================= #


# ================START================ #
# ================四  川================ #

# 四川政府采购
@add_url(url_filter("http://www.sczfcg.com/CmsNewsController.do"))
def sc_zfcg_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.sczfcg.com"
    bs = build_beautiful_soup(html)
    lst = bs.find("div", attrs={"class": "colsList"}).find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        t = item.find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t["title"]
        info[PUBLISHED_TS] = extract_first_date(item.find("span").get_text(), is_str=True)
        links.append(info)

    pager = bs.find("div", attrs={"class": "flipPage"})
    pages = re.findall("\d+/\d+", pager.get_text())[0]
    current_page, total_page = pages.split("/")
    current_page = int(current_page)
    total_page = int(total_page)
    while current_page < total_page:
        next_page_info = copy.deepcopy(pre_information)
        next_page_info[URL] = re.sub("page\=\d+", "page=%s" % (current_page + 1), next_page_info[URL])
        if pre_information.get(GENERATE_ALL_PAGE):  # 判断是否直接生成后面所有目录页地址
            next_page_info[GENERATED_PAGE] = total_page
            links.append(next_page_info)
            current_page += 1
        else:
            links.append(next_page_info)
            break

    return links, contents


@add_url(url_filter("http://www.sczfcg.com/view/staticpags/"))
def sc_zfcg_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("table")
    time = bs.find("div", attrs={"class": "reportTitle"}).find("span")
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)
    info[PUBLISHED_TS] = extract_first_date(time.get_text(), is_str=True)
    contents.append(info)

    trs = content.find_all("tr")
    t = [tr for tr in trs if len(tr.find_all("td")) == 2]
    summary = {}
    if len(t) > 0:
        tds = content.find_all("td")
        for i in range(len(tds) / 2):
            k = tds[2 * i].get_text().strip()
            v = tds[2 * i + 1].get_text().strip()
            if len(k) > 0 and len(v) > 0:
                summary[k] = v

    # info[PROJECT_NAME] = summary.get(u"采购项目名称")
    # info[PROJECT_ID] = summary.get(u"采购项目编号")
    # info[PURCHASE_TYPE] = summary.get(u"采购方式")
    # info[PURCHASER_NAME] = summary.get(u"采购人")
    # info[AGENT_NAME] = summary.get(u"采购代理机构名称")
    # info[TOTAl_WINNING_MONEY_AMOUNT] = summary.get(u"采购结果总金额")
    # info[WINNING_TS] = summary.get(u"定标日期")
    # info[EXPERT_NAMES] = summary.get(u"评审委员会成员名单")
    #
    # for key in summary.keys():
    #     if key in [u"采购项目名称"]:
    #         del summary[key]
    info[OTHERS] = summary

    return links, contents


# ================四  川================ #
# =================END================= #


# ================START================ #
# ================江  西================ #

# 江西招标信息网
@add_url(url_filter("http://jx.hzzhaobiao.com/zhongbiao.asp"))
def jx_zbxxw_ml(html, pre_information):
    links, contents = [], []

    html = html.decode(encoding="gbk")
    host = "http://jx.hzzhaobiao.com"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find("table", attrs={"class": "border"}).find_all("tr")
    for item in lst:
        info = copy.deepcopy(pre_information)
        tds = item.find_all("td")
        t = tds[0].find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t.get_text().strip()
        info[REGION] = pre_information[ORIGIN_REGION] + ">>" + tds[1].get_text().strip()
        info[PUBLISHED_TS] = extract_first_date(tds[2].get_text(), is_str=True)
        links.append(info)

    # 找到所有目录后面页地址
    current_page = re.findall("(?<=page\=)\d+", pre_information[URL])
    if len(current_page) == 0:
        current_page = 1
    else:
        current_page = int(current_page[0])
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    pager = bs.find("form", attrs={"name": "theform"})
    total_page = re.findall(u"(?<=共)\d+(?=页)", pager.get_text())
    total_page = int(total_page[0])

    def next_page_func(info, next_page):
        info[URL] = re.sub("page\=\d+", "page=%s" % next_page, pre_information[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://jx.hzzhaobiao.com/news1/"))
def jx_zbxxw_nr(html, pre_information):
    links, contents = [], []

    html = html.decode(encoding="gbk")
    bs = build_beautiful_soup(html)
    t = bs.find("table")
    t = [k for k in t.contents if isinstance(k, type(t)) and k.name == "tr"]
    content = t[-1]
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# 江西省政府采购网
@add_url(url_filter("http://ggzy.jiangxi.gov.cn/jxzbw/jyxx/%s/%s/%s", "\d+", "\d+", "$"))
def jx_zbxxw_ml(html, pre_information):
    links, contents = [], []
    return links, contents


@add_url(url_filter("http://ggzy.jiangxi.gov.cn/jxzbw/%s/%s/%s/MoreInfo.aspx", "[a-zA-Z]+", "\d+", "\d+"))
def jx_zbxxw_ml(html, pre_information):
    links, contents = [], []

    host = "http://ggzy.jiangxi.gov.cn"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find("table", id="MoreInfoList1_DataGrid1").find_all("tr")
    for item in lst:
        info = copy.deepcopy(pre_information)
        tds = item.find_all("td")
        t = tds[1].find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t["title"]
        t = tds[1].find("font")
        if t:
            info[REGION] = pre_information[ORIGIN_REGION] + ">>" + t.get_text().strip()
        info[PUBLISHED_TS] = extract_first_date(tds[2].get_text(), is_str=True)
        info[METHOD] = GET
        if PARAMS in info:
            del info[PARAMS]
        links.append(info)

    # 找到所有目录后面页地址
    if PARAMS in pre_information and "__EVENTARGUMENT" in pre_information[PARAMS]:
        current_page = pre_information[PARAMS]["__EVENTARGUMENT"]
    else:
        current_page = 1
    pager = bs.find("div", id="MoreInfoList1_Pager")
    total_page = re.findall(u"(?<=总页数：)\d+", pager.get_text())
    total_page = int(total_page[0])

    def next_page_func(info, next_page):
        state = bs.find("input", id="__VIEWSTATE")["value"]
        if info.get(METHOD, "") != POST:
            info[METHOD] = POST
        if not info.get(PARAMS):
            info[PARAMS] = {
                "__VIEWSTATE": state,
                "__EVENTTARGET": "MoreInfoList1$Pager",
                "__EVENTARGUMENT": 1
            }
        info[PARAMS]["__EVENTARGUMENT"] = next_page

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://ggzy.jiangxi.gov.cn/jxzbw/ZtbInfo/ZBGG_Detail.aspx"))
@add_url(url_filter("http://ggzy.jiangxi.gov.cn/jxzbw/InfoDetail/Default.aspx"))
def jx_zbxxw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("td", id="TDContent")
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================江  西================ #
# =================END================= #


# ================START================ #
# ================福  建================ #

# 福建省政府采购网
@add_url(url_filter("http://cz.fjzfcg.gov.cn/web/fjsindex/index.html"))
def fj_zfcgw_idx(html, pre_information):
    links, contents = [], []
    return links, contents


@add_url(url_filter("http://cz.fjzfcg.gov.cn/n/webfjs/queryPageData.do"))
def fj_zfcgw_ml(html, pre_information):
    links, contents = [], []

    host = "http://cz.fjzfcg.gov.cn/n/webfjs/article.do?noticeId="
    # 找到所有列表项目地址
    data = json.loads(html)
    lst = data.get("list")
    for item in lst:
        info = copy.deepcopy(pre_information)
        info[URL] = host + item[u'noticeId']
        info[DATA_URL] = "http://cz.fjzfcg.gov.cn/n/noticemgr/query-viewcontentfj.do"
        info[PARAMS]["noticeId"] = item[u'noticeId']
        info[TITLE] = item[u'title']
        if u'areaName' in item:
            info[REGION] = pre_information[ORIGIN_REGION] + ">>" + item["areaName"]
        if u'time' in item:
            info[PUBLISHED_TS] = datetime.datetime.strptime(item["time"], "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        links.append(info)

    # 找到所有目录后面页地址
    current_page = pre_information[PARAMS]["page"]
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    total_page = current_page
    if len(lst) > 0:
        total_page = current_page + 1

    def next_page_func(info, next_page):
        info[PARAMS]["page"] = next_page

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://cz.fjzfcg.gov.cn/n/noticemgr/query-viewcontentfj.do"))
def fj_zfcgw_nr(html, pre_information):
    links, contents = [], []

    content = html
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================福  建================ #
# =================END================= #


# ================START================ #
# ================安  徽================ #

# 安徽省政府采购网
@add_url(
    url_filter("http://www.ccgp-anhui.gov.cn/mhxt/MhxtSearchBulletinController.zc?method=bulletinChannelRightDown"))
def ah_zfcgw_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.ccgp-anhui.gov.cn/"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find("div", attrs={"class": "column infoLink noBox addState addStateL unitWidth_x6"}).find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        info[METHOD] = GET
        t = item.find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t.get_text().strip()
        t = item.find("span")
        info[PUBLISHED_TS] = extract_first_date(t.get_text(), is_str=True)
        links.append(info)

    # 找到所有目录后面页地址
    current_page = pre_information[PARAMS]["pageNo"]
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    total_page = current_page
    if len(lst) > 0:
        total_page = current_page + 1

    def next_page_func(info, next_page):
        info[PARAMS]["pageNo"] = next_page

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.ccgp-anhui.gov.cn/news/"))
def ah_zfcgw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", attrs={"class": "frameNews"})
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================安  徽================ #
# =================END================= #


# ================START================ #
# ================浙  江================ #

# 浙江政府采购网
@add_url(url_filter("http://www.zjzfcg.gov.cn/new/articleSearch"))
def zj_zfcgw_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.zjzfcg.gov.cn/new"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find("div", id="tigtag2_right").find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        t = item.find_all("a")
        if not t[2]["href"].startswith(".."):
            continue
        info[URL] = host + t[2]["href"][2:]
        info[TITLE] = t[2]["title"]

        info[REGION] = info[ORIGIN_REGION] + ">>" + t[0].get_text().strip("[] ")
        info[PURCHASE_CATEGORY] = t[1].get_text().strip("[] ")

        links.append(info)

    # 找到所有目录后面页地址
    current_page = re.findall("\d+", pre_information[URL])
    if len(current_page) > 0:
        current_page = int(current_page[0])
    else:
        current_page = 1
    total_page = current_page
    if len(lst) > 0:
        total_page = current_page + 1

    def next_page_func(info, next_page):
        info[URL] = re.sub("(?<=search_)\d+", str(next_page), info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.zjzfcg.gov.cn/new/%s/%s.html", "[a-z]+", "\d+"))
def zj_zfcgw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", id="news_content")
    p_time = bs.find("div", id="news_msg")
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)
    info[PUBLISHED_TS] = extract_first_date(p_time.get_text())

    contents.append(info)

    return links, contents


# ================浙  江================ #
# =================END================= #

# ================START================ #
# ================江  苏================ #

# 江苏政府采购网
@add_url(url_filter("http://www.ccgp-jiangsu.gov.cn/pub/jszfcg/cgxx/cjgg/index"))
def zj_zfcgw_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.ccgp-jiangsu.gov.cn/pub/jszfcg/cgxx/cjgg"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find("div", attrs={"class": "list_list"}).find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        info[METHOD] = GET
        t = item.find("a")
        info[URL] = host + t["href"][1:]
        info[TITLE] = t.get_text().strip()
        t = re.sub("\s", "", item.get_text())[-10:]
        info[PUBLISHED_TS] = extract_first_date(t)
        links.append(info)

    # 找到所有目录后面页地址
    current_page = re.findall("\d+", pre_information[URL])
    if len(current_page) == 0:
        current_page = 1
    else:
        current_page = int(current_page[0]) + 1
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    pager = bs.find("div", attrs={"class": "fanye"})
    total_page = int(re.findall("\d+", pager.get_text())[0])

    def next_page_func(info, next_page):
        info[URL] = re.sub("index(_\d+|)", "index_%s" % (next_page - 1), info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.ccgp-jiangsu.gov.cn/pub/jszfcg/cgxx/cjgg/%s/", "\d+"))
def zj_zfcgw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", attrs={"class": "detail_con"})
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================江  苏================ #
# =================END================= #

# ================START================ #
# ================吉  林================ #
# TODO PROJECT_TYPE 规整
# 吉林省公共资源交易信息网
@add_url(url_filter("http://ggzyjy.jl.gov.cn/JiLinZtb//Template/Default/MoreInfoJYXX.aspx?CategoryNum=004002"))
def jl_ggzyjyxxw_ml(html, pre_information):
    links, contents = [], []

    host = "http://ggzyjy.jl.gov.cn/JiLinZtb//"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find("table", id="DataList1").find_all("tr")
    if len(lst) > 0 and len(lst) % 2 == 0:
        lst = [lst[i] for i in range(1, len(lst), 2)]
    for item in lst:
        info = copy.deepcopy(pre_information)
        info[METHOD] = GET
        if PARAMS in info:
            del info[PARAMS]
        tds = item.find_all("td")
        t = tds[1].find("a")
        info[URL] = host + t["href"].lstrip("../../")
        info[TITLE] = t["title"]
        p_typ = tds[2].get_text().strip("[] \n\r")
        if u"工程" in p_typ:
            info[PROJECT_TYPE] = u"工程建设"
        elif u"土地" in p_typ:
            info[PROJECT_TYPE] = u"土地交易"
        info[REGION] = info[ORIGIN_REGION] + ">>" + tds[3].get_text().strip("[] \n\r")
        info[PUBLISHED_TS] = extract_first_date(tds[4].get_text())
        links.append(info)

    # 找到所有目录后面页地址
    if PARAMS in pre_information and "__EVENTARGUMENT" in pre_information[PARAMS]:
        current_page = pre_information[PARAMS]["__EVENTARGUMENT"]
    else:
        current_page = 1
    pager = bs.find("div", attrs={"id": "Pager"})
    total_page = int(re.findall(u"\d+", pager.get_text())[1])

    def next_page_func(info, next_page):
        view_state_tag = bs.find("input", id="__VIEWSTATE")
        view_state = view_state_tag["value"]
        envent_validation_tag = bs.find("input", id="__EVENTVALIDATION")
        envent_validation = envent_validation_tag["value"]
        info[METHOD] = POST
        param = {
            "__EVENTTARGET": "Pager",
            "__EVENTARGUMENT": next_page,
            "__VIEWSTATE": view_state,
            "__EVENTVALIDATION": envent_validation,
        }
        info[PARAMS] = param

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://ggzyjy.jl.gov.cn/JiLinZtb//infodetail/"))
def jl_ggzyjyxxw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("td", attrs={"id": "TDContent"})
    # content = ""
    # for it in its:
    #     content += it.prettify()

    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================吉  林================ #
# =================END================= #

# ================START================ #
# ================辽  宁================ #

# 辽宁省政府集中采购网
@add_url(url_filter("http://www.lnzc.gov.cn/SitePages/AfficheListAll2.aspx"))
def ln_zfjzcgw_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.lnzc.gov.cn"
    bs = build_beautiful_soup(html)
    lst = bs.find("div", attrs={
        "id": "WebPartctl00_ctl00_ContentPlaceHolderMain_ContentPlaceHolderMain_g_8ac3be76_5de3_4bbf_a034_d924bd6995c5"}).find_all(
        "li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        info[METHOD] = GET
        t = item.find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t["title"]
        t = item.find("span", attrs={"class": "listDate"})
        try:
            info[PUBLISHED_TS] = datetime.datetime.strptime(t.get_text().strip(), "%Y/%m/%d").strftime(
                "%Y-%m-%d %H:%M:%S")
        except:
            pass
        links.append(info)

    # 找到所有目录后面页地址
    pager = bs.find("td", attrs={"class": "ms-paging"})
    page = pager.find_all("a")
    if len(page) == 1 or len(page) == 3:
        href = page[len(page) - 1]["href"]
        params = re.findall(u"'.*?'", href)
        if len(params) == 2:
            next_page_info = copy.deepcopy(pre_information)
            next_page_info[PARAMS]["__EVENTARGUMENT"] = params[1]
            links.append(next_page_info)

    return links, contents


@add_url(url_filter("http://www.lnzc.gov.cn/oa/bs/SitePages/AfficheDetail_sel.aspx"))
def ln_zfjzcgw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", attrs={"class": "col-xs-12 article"})
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================辽  宁================ #
# =================END================= #

# ================START================ #
# ================黑龙江================ #
# 黑龙江省政府采购网
@add_url(url_filter("http://www.hljcg.gov.cn/xwzs!index.action"))
def hlj_zfcgw_ml(html, pre_information):
    links, contents = [], []
    return links, contents


@add_url(url_filter("http://www.hljcg.gov.cn/xwzs!queryXwxxqx.action?lbbh=5"))
@add_url(url_filter("http://www.hljcg.gov.cn/xwzs!queryXwxxqx.action"))
def hlj_zfcgw_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.hljcg.gov.cn"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find_all("div", attrs={"class": "xxei"})
    for item in lst:
        info = copy.deepcopy(pre_information)
        info[METHOD] = GET
        if PARAMS in info:
            del info[PARAMS]
        t = item.find("a")
        url = re.findall("'.*'", t["onclick"])[0].strip("'")
        info[URL] = host + url
        info[TITLE] = t.get_text().strip()
        t = item.find("span", attrs={"class": "sjej"})
        info[PUBLISHED_TS] = extract_first_date(t.get_text())
        links.append(info)

    # 找到所有目录后面页地址
    pager = bs.find("div", attrs={"class": "list-page-detail"})
    current_page = int(re.findall(u"\d+(?=/)", pager.get_text())[0])
    total_page = int(re.findall(u"(?<=/)\d+", pager.get_text())[0])

    def next_page_func(info, next_page):
        # info[URL] = re.sub("xwzsPage.pageNo\=\d+", "xwzsPage.pageNo=%s" % next_page, info[URL])
        param = {
            "xwzsPage.pageNo": next_page,
            "xwzsPage.pageSize": 20,
            "xwzsPage.pageCount": 1611,
            "lbbh": "",
            "xwzsPage.LBBH": ""
        }
        info[METHOD] = POST
        info[PARAMS] = param

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.hljcg.gov.cn/xwzs!queryOneXwxxqx.action"))
def hlj_zfcgw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", attrs={"style": " margin-top:10px;border-top:#bbb dotted 1px;   padding-top:10px; "})
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================黑龙江================ #
# =================END================= #

# ================START================ #
# ================湖  南================ #

# 湖南省政府采购网
@add_url(url_filter("http://www.ccgp-hunan.gov.cn/mvc/getNoticeList4Web.do"))
def hn_zfcgw_ml(html, pre_information):
    links, contents = [], []
    host = "http://www.ccgp-hunan.gov.cn/page/notice/notice.jsp?noticeId="
    host_ = "http://www.ccgp-hunan.gov.cn/mvc/viewNoticeContent.do?area_id=&noticeId="
    # 找到所有列表项目地址
    try:
        data = json.loads(unicode(html), strict=False)
        pre_information[SLEEP_SECOND] = 1
    except Exception, e:
        print e.message
        info = copy.deepcopy(pre_information)
        info[SLEEP_SECOND] = min(16, info[SLEEP_SECOND] * 2)
        info[CRAWLED_COUNT] = 0
        return [info], []

    lst = data.get("rows", [])
    for item in lst:
        info = copy.deepcopy(pre_information)
        info[METHOD] = GET
        del info[SLEEP_SECOND]
        if u'NOTICE_ID' not in item:
            continue
        info[URL] = host + str(item[u'NOTICE_ID'])
        info[DATA_URL] = host_ + str(item[u'NOTICE_ID'])
        info[TITLE] = item.get(u'NOTICE_TITLE')
        info[PUBLISHED_TS] = item.get(u'NEWWORK_DATE')
        info[PROJECT_ID] = item.get(u'PRCM_PLAN_NO')
        links.append(info)

    # 找到所有目录后面页地址
    current_page = pre_information[PARAMS]["page"]
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))

    if TOTAl_PAGE in pre_information:
        total_page = pre_information[TOTAl_PAGE]
    else:
        try:
            import math
            total_page = data.get("total", current_page)
            total_page = int(math.ceil(int(total_page) * 1.0 / pre_information[PARAMS]["pageSize"]))
            pre_information[TOTAl_PAGE] = total_page
        except Exception, e:
            total_page = current_page
            if len(lst) > 0:
                total_page = current_page + 1

    def next_page_func(info, next_page):
        info[PARAMS]["page"] = next_page

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.ccgp-hunan.gov.cn/mvc/getNoticeListOfCityCounty.do"))
def hn_zfcgw_ml(html, pre_information):
    links, contents = [], []
    host = "http://www.ccgp-hunan.gov.cn/page/notice/notice.jsp?area_id=1&noticeId="
    host_ = "http://www.ccgp-hunan.gov.cn/mvc/viewNoticeContent.do?area_id=1&noticeId="
    # 找到所有列表项目地址
    try:
        lst = json.loads(unicode(html), strict=False)
        pre_information[SLEEP_SECOND] = 1
    except Exception, e:
        print e.message
        info = copy.deepcopy(pre_information)
        info[SLEEP_SECOND] = min(16, info[SLEEP_SECOND] * 2)
        info[CRAWLED_COUNT] = 0
        return [info], []

    for item in lst:
        info = copy.deepcopy(pre_information)
        info[METHOD] = GET
        del info[SLEEP_SECOND]
        if u'NOTICE_ID' not in item:
            continue
        info[URL] = host + str(item[u'NOTICE_ID'])
        info[DATA_URL] = host_ + str(item[u'NOTICE_ID'])
        info[TITLE] = item.get(u'NOTICE_TITLE')
        info[PUBLISHED_TS] = item.get(u'NEWWORK_DATE')
        info[PROJECT_ID] = item.get(u'PRCM_PLAN_NO')
        info[REGION] = pre_information[ORIGIN_REGION] + ">>" + item.get(u'AREA_NAME', "")
        links.append(info)

    # 找到所有目录后面页地址
    current_page = pre_information[PARAMS]["page"]
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))

    total_page = current_page
    if len(lst) > 0:
        total_page = current_page + 1

    def next_page_func(info, next_page):
        info[PARAMS]["page"] = next_page

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.ccgp-hunan.gov.cn/mvc/viewNoticeContent.do?area_id=&noticeId="))
def hn_zfcgw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("table")
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


@add_url(url_filter("http://www.ccgp-hunan.gov.cn/mvc/viewNoticeContent.do?area_id=1&noticeId="))
def hn_zfcgw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div")
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================湖  南================ #
# =================END================= #

# ================START================ #
# ================湖  北================ #

# 湖北招标网
@add_url(url_filter("http://www.hbzbw.com/zhongbiao.asp?page=%s", "\d+"))
def hb_zbxxw_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.hbzbw.com"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find("table", attrs={"class": "border"}).find_all("tr")
    for item in lst:
        info = copy.deepcopy(pre_information)
        tds = item.find_all("td")
        t = tds[0].find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t.get_text().strip()
        info[REGION] = info[ORIGIN_REGION] + ">>" + tds[1].get_text().strip()
        info[PUBLISHED_TS] = extract_first_date(tds[2].get_text())
        links.append(info)

    # 找到所有目录后面页地址
    current_page = re.findall("(?<=page\=)\d+", pre_information[URL])
    if len(current_page) == 0:
        current_page = 1
    else:
        current_page = int(current_page[0])
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    pager = bs.find("table", attrs={"class": "border", "align": "center", "border": "0", "width": "98%"})
    total_page = int(re.findall(u"(?<=共)\d+(?=页)", pager.get_text())[0])

    def next_page_func(info, next_page):
        info[URL] = re.sub("page\=\d+", "page=%s" % next_page, info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.hbzbw.com/news1/"))
def hb_zbxxw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", attrs={"align": "center"})
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================湖  北================ #
# =================END================= #

# ================START================ #
# ================陕  西================ #

# 陕西招标信息网
@add_url(url_filter("http://www.sxzhaobiao.com/zhongbiao.asp?page="))
def sx_zbxxw_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.sxzhaobiao.com"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find("table", attrs={"class": "border"}).find_all("tr")
    for item in lst:
        info = copy.deepcopy(pre_information)
        tds = item.find_all("td")
        t = tds[0].find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t.get_text().strip()
        info[REGION] = info[ORIGIN_REGION] + ">>" + tds[1].get_text().strip()
        info[PUBLISHED_TS] = extract_first_date(tds[2].get_text())
        links.append(info)

    # 找到所有目录后面页地址
    current_page = re.findall("(?<=page\=)\d+", pre_information[URL])
    if len(current_page) == 0:
        current_page = 1
    else:
        current_page = int(current_page[0])
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    pager = bs.find("table", attrs={"class": "border", "align": "center", "border": "0", "width": "98%"})
    total_page = int(re.findall(u"(?<=共)\d+(?=页)", pager.get_text())[0])

    def next_page_func(info, next_page):
        info[URL] = re.sub("page\=\d+", "page=%s" % next_page, info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.sxzhaobiao.com/news1/"))
def sx_zbxxw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", attrs={"align": "center"})
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================陕  西================ #
# =================END================= #

# ================START================ #
# ================山  东================ #

# 山东招标采购网
@add_url(url_filter("http://www.sdzbcg.com/zhongbiao.asp?page="))
def sd_zbxxw_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.sdzbcg.com"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find("table", attrs={"class": "border"}).find_all("tr")
    for item in lst:
        info = copy.deepcopy(pre_information)
        tds = item.find_all("td")
        t = tds[0].find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t.get_text().strip()
        info[REGION] = info[ORIGIN_REGION] + ">>" + tds[1].get_text().strip()
        info[PUBLISHED_TS] = extract_first_date(tds[2].get_text())
        links.append(info)

    # 找到所有目录后面页地址
    current_page = re.findall("(?<=page\=)\d+", pre_information[URL])
    if len(current_page) == 0:
        current_page = 1
    else:
        current_page = int(current_page[0])
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    pager = bs.find("table", attrs={"class": "border", "align": "center", "border": "0", "width": "98%"})
    total_page = int(re.findall(u"(?<=共)\d+(?=页)", pager.get_text())[0])

    def next_page_func(info, next_page):
        info[URL] = re.sub("page\=\d+", "page=%s" % next_page, info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.sdzbcg.com/news1/"))
def sd_zbxxw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", attrs={"align": "center"})
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================山  东================ #
# =================END================= #

# ================START================ #
# ================山  西================ #
# TODO

# 中国山西政府采购网
@add_url(url_filter("http://www.ccgp-shanxi.gov.cn/view.php?nav=104"))
def sx_zgsxzfcgw_ml(html, pre_information):
    links, contents = [], []

    host = u"http://www.ccgp-shanxi.gov.cn/"
    bs = build_beautiful_soup(html)
    try:
        lst = bs.find("table", id="node_list").find("tbody").find_all("tr")
    except:
        return [pre_information], []
    for item in lst:
        info = copy.deepcopy(pre_information)
        del info[SLEEP_SECOND]
        tds = item.find_all("td")
        if len(tds[0].get_text().strip()) == 0:
            continue
        t = tds[0].find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t["title"]
        info[PUBLISHED_TS] = extract_first_date(tds[3].get_text(), is_str=True)
        region = tds[1].get_text().strip()
        if len(region):
            info[REGION] = u"山西>>" + region
        else:
            info[REGION] = u"山西"
        links.append(info)

    # 找到所有目录后面页地址
    pager = bs.find("div", attrs={"class": "pager"})
    t = re.findall("\d+", pager.get_text().strip())
    current_page = int(t[0])
    total_page = int(t[1])

    def next_page_func(info, next_page):
        if "page" in info[URL]:
            info[URL] = re.sub("page\=\d+", "page=%s" % next_page, info[URL])
        else:
            info[URL] += "&page=%s" % next_page

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.ccgp-shanxi.gov.cn/view.php?nid="))
def sx_zgsxzfcgw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", id="div_view")
    pro_id = bs.find("font", attrs={"color": "#F00000"})
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    if pro_id:
        pro_id = pro_id.get_text().strip()
        pro_id = re.findall(u"(?<=招标编号：).*", pro_id)
        if len(pro_id) > 0:
            info[PROJECT_ID] = pro_id[0]

    contents.append(info)

    return links, contents


# ================山  西================ #
# =================END================= #


# ================START================ #
# ================河  南================ #

# 河南招标信息网
@add_url(url_filter("http://www.hnzhaobiao.com/zhongbiao.asp?page="))
def hn_zbxxw_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.hnzhaobiao.com"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find("table",
                  attrs={"bgcolor": "#E8E8E8", "border": "0", "width": "600", "cellpadding": "3",
                         "cellspacing": "1"}).find_all("tr")[1:-1]
    for item in lst:
        info = copy.deepcopy(pre_information)
        tds = item.find_all("td")
        t = tds[0].find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t.get_text().strip()
        info[REGION] = info[ORIGIN_REGION] + ">>" + tds[1].get_text().strip()
        info[PUBLISHED_TS] = extract_first_date(tds[2].get_text())
        links.append(info)

    # 找到所有目录后面页地址
    current_page = re.findall("(?<=page\=)\d+", pre_information[URL])
    if len(current_page) == 0:
        current_page = 1
    else:
        current_page = int(current_page[0])
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    pager = bs.find("form", attrs={"name": "theform", "method": "get"})
    total_page = int(re.findall(u"(?<=共)\d+(?=页)", pager.get_text())[0])

    def next_page_func(info, next_page):
        info[URL] = re.sub("page\=\d+", "page=%s" % next_page, info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.hnzhaobiao.com/news1/"))
def hn_zbxxw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("td", attrs={"align": "left", "height": 510, "valign": "top", "width": "847"})
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================河  南================ #
# =================END================= #


# ================START================ #
# ================河  北================ #
# TODO
# 河北省招标投标综合网

# 河北省省级政府采购中心
@add_url(url_filter("http://www.hbgp.gov.cn/046/%s.html", "\d+"))
def hb_sjzfcgzx_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.hbgp.gov.cn"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find("div", attrs={"id": "categorypagingcontent"}).find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        t = item.find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t["title"]
        t = item.find("span")
        info[PUBLISHED_TS] = extract_first_date(t.get_text())
        links.append(info)

    # 找到所有目录后面页地址
    pager = bs.find("div", attrs={"class": "pagemargin"})
    pages = re.findall("\d+/\d+", pager.get_text())[0]
    pages = pages.split("/")
    current_page = int(pages[0])
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    total_page = int(pages[1])

    def next_page_func(info, next_page):
        info[URL] = re.sub("\d+\.html", "%s.html" % next_page, info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.hbgp.gov.cn/046/%s/%s.html", "\d+", "[\w\-]+"))
def hb_sjzfcgzx_nr(html, pre_information):
    links, contents = [], []

    # html = html_purify(html)
    bs = build_beautiful_soup(html)
    content = bs.find("table")
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# 河北省公共资源交易中心
@add_url(url_filter("http://www.hebggzy.cn/002/002009/002009001/002009001006/%s.html", "\d+"))
@add_url(url_filter("http://www.hebggzy.cn/002/002009/002009002/002009002003/%s.html", "\d+"))
def hb_ggzyjyzx_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.hebggzy.cn"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find("div", attrs={"id": "categorypagingcontent"}).find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        t = item.find("a")
        info[URL] = host + t["href"]
        t = item.find("div", attrs={"class": "frame-con-txt l"})
        info[TITLE] = t.get_text().strip()
        t = item.find("span")
        info[PUBLISHED_TS] = extract_first_date(t.get_text())
        links.append(info)

    # 找到所有目录后面页地址
    pager = bs.find("div", attrs={"class": "pagemargin"})
    pages = re.findall("\d+/\d+", pager.get_text())[0]
    pages = pages.split("/")
    current_page = int(pages[0])
    total_page = int(pages[1])

    def next_page_func(info, next_page):
        info[URL] = re.sub("\d+\.html", "%s.html" % next_page, info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.hebggzy.cn/002/002009/002009001/002009001006/%s/%s.html", "\d+", "[\w\-]+"))
@add_url(url_filter("http://www.hebggzy.cn/002/002009/002009002/002009002003/%s/%s.html", "\d+", "[\w\-]+"))
def hb_sjzfcgzx_nr(html, pre_information):
    links, contents = [], []

    # html = html_purify(html)
    bs = build_beautiful_soup(html)
    summary = bs.find("div", attrs={"class": "show-con infoContent"})
    content = bs.find("table")
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = "<div>%s</div>" % (str(summary) + str(content))

    contents.append(info)

    return links, contents


# 河北省公共资源交易服务平台
@add_url(url_filter("http://www.hebpr.cn/002/002009/002009001/002009001005/%s.html", "\d+"))
@add_url(url_filter("http://www.hebpr.cn/002/002009/002009001/002009001006/%s.html", "\d+"))
@add_url(url_filter("http://www.hebpr.cn/002/002009/002009002/002009002003/%s.html", "\d+"))
@add_url(url_filter("http://www.hebpr.cn/002/002009/002009002/002009002005/%s.html", "\d+"))
def hb_ggzyjyfwpt_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.hebpr.cn"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find("div", attrs={"id": "categorypagingcontent"}).find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        t = item.find("a")
        info[URL] = host + t["href"]
        t = item.find("p", attrs={"class": "now-link-title l"})
        info[TITLE] = t.get_text().strip()
        t = item.find("span")
        info[PUBLISHED_TS] = extract_first_date(t.get_text())
        links.append(info)
        rg = re.findall(u"^【([\u4e00-\u9fa5]+)】", info[TITLE])
        if rg:
            info[REGION] = info[ORIGIN_REGION] + u">>" + rg[0]

    # 找到所有目录后面页地址
    pager = bs.find("div", attrs={"class": "pagemargin"})
    pages = re.findall("\d+/\d+", pager.get_text())[0]
    pages = pages.split("/")
    current_page = int(pages[0])
    total_page = int(pages[1])

    def next_page_func(info, next_page):
        info[URL] = re.sub("\d+\.html", "%s.html" % next_page, info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.hebpr.cn/002/002009/002009001/002009001005/%s/%s.html", "\d+", "[\w\-]+"))
@add_url(url_filter("http://www.hebpr.cn/002/002009/002009001/002009001006/%s/%s.html", "\d+", "[\w\-]+"))
@add_url(url_filter("http://www.hebpr.cn/002/002009/002009002/002009002003/%s/%s.html", "\d+", "[\w\-]+"))
@add_url(url_filter("http://www.hebpr.cn/002/002009/002009002/002009002005/%s/%s.html", "\d+", "[\w\-]+"))
def hb_ggzyjyfwpt_nr(html, pre_information):
    links, contents = [], []

    # html = html_purify(html)
    bs = build_beautiful_soup(html)
    summary = bs.find("div", attrs={"class": "sub-title"})
    content = bs.find("div", attrs={"class": "show-con infoContent"})
    suma = summary.get_text()
    rg = re.findall(u"【信息来源：([\u4e00-\u9fa5]+)】", suma)
    ts = re.findall(u"【信息时间：([\d\-: ]+) 阅读次数：", suma)
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)
    if rg:
        if rg[0] not in info.get(REGION, ""):
            info[REGION] = info[ORIGIN_REGION] + u">>" + rg[0]
    if ts:
        info[PUBLISHED_TS] = extract_first_date(ts[0])

    contents.append(info)

    return links, contents


# 河北省政府采购网
@add_url(url_filter("http://www.ccgp-hebei.gov.cn/zfcg/web/getPreWinAnncList_%s.html", "\d+"))
@add_url(url_filter("http://www.ccgp-hebei.gov.cn/zfcg/web/getBidWinAnncList_%s.html", "\d+"))
def hb_zfcgw_ml(html, pre_information):
    links, contents = [], []

    if "Pre" in pre_information[URL]:
        host = "http://www.ccgp-hebei.gov.cn/zfcg/preBidingAnncDetail_{}.html"
    else:
        host = "http://www.ccgp-hebei.gov.cn/zfcg/bidWinAnncDetail_{}.html"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    t = bs.find("table", attrs={"width": "750", "border": "0", "align": "center", "cellpadding": "0",
                                "cellspacing": "0"})
    lst = t.find_all("tr")
    for idx in range(0, len(lst) - 1, 2):
        tt = lst[idx]
        summary = lst[idx + 1]
        info = copy.deepcopy(pre_information)
        id_ = re.findall("\d+", tt.attrs["onclick"])
        info[URL] = host.format(id_[0])
        t = tt.find('a')
        info[TITLE] = t.get_text().strip()
        t = summary.find('td', attrs={"class": "txt1"})
        txt = re.sub(u"[\s 　]+", u"", t.get_text().strip())
        sums = re.findall(u"发布时间：([\d\-]*)地域：([\u4e00-\u9fa5]*)采购人：([\u4e00-\u9fa5]*)", txt)
        if sums:
            info[PUBLISHED_TS] = extract_first_date(sums[0][0])
            info[PURCHASER_ADDRESS] = sums[0][1]
            info[PURCHASER_NAME] = sums[0][2]
        links.append(info)

    # 找到所有目录后面页地址
    pager = bs.find("head")
    pages = re.sub(u"[\s 　]+", u"", unicode(pager))
    pages = re.findall(u'pageFenye\("(\d+)","(\d+)"', pages)
    current_page = int(pages[0][0])
    total_page = int(pages[0][1])

    def next_page_func(info, next_page):
        info[URL] = re.sub("\d+\.html", "%s.html" % next_page, info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.ccgp-hebei.gov.cn/zfcg/preBidingAnncDetail_%s.html", "\d+"))
@add_url(url_filter("http://www.ccgp-hebei.gov.cn/zfcg/bidWinAnncDetail_%s.html", "\d+"))
def hb_zfcgw_nr(html, pre_information):
    links, contents = [], []

    # html = html_purify(html)
    bs = build_beautiful_soup(html)
    summary = bs.find("table", attrs={"width": "930", "border": "0", "align": "center",
                                      "cellpadding": "0", "cellspacing": "1", "bgcolor": "#bfdff1"})
    content = bs.find("table", attrs={"width": "930", "border": "0", "align": "center",
                                      "cellpadding": "0", "cellspacing": "0"})
    tds = summary.find_all("td")
    sums = {}
    for idx in range(0, len(tds), 2):
        k = tds[idx].get_text().strip().strip(u"：:")
        v = tds[idx + 1].get_text().strip()
        sums[k] = v
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        info[CONTENT] = str(html_purify(content))
    info[CONTENT] = str(content)

    if u"采购方式" in sums:
        info[PURCHASE_TYPE] = sums.pop(u"采购方式")
    if u"项目名称" in sums:
        info[PROJECT_NAME] = sums.pop(u"项目名称")
    if u"项目联系人" in sums:
        info[PROJECT_CONTACT_NAME] = sums.pop(u"项目联系人")
    if u"联系方式" in sums:
        info[PROJECT_CONTACT_PHONE] = sums.pop(u"联系方式")
    if u"代理机构" in sums:
        info[AGENT_NAME] = sums.pop(u"代理机构")
    info[OTHERS] = sums

    if not info.get(PUBLISHED_TS):
        info[PUBLISHED_TS] = extract_first_date(content.get_text())

    contents.append(info)

    return links, contents


# 石家庄工程建设交易信息网
@add_url(url_filter("http://www.sjzjzsc.com/ZBGS.ASPX?pages=%s", "\d+"))
def hb_zfcgw_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.sjzjzsc.com/"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    t = bs.find("ul", attrs={"class": "Article_List_GG"})
    lst = t.find_all("li")
    if lst and lst[0]["class"] == ["title"]:
        lst = lst[1:]
    for item in lst:
        sps = item.find_all("span")
        info = copy.deepcopy(pre_information)
        info[PROJECT_ID] = sps[0].get_text().strip()
        t = sps[1].find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t["title"]
        rg = sps[2].get_text().strip()
        if rg:
            if rg not in info[ORIGIN_REGION]:
                info[REGION] = info[ORIGIN_REGION] + u">>" + rg
        info[PUBLISHED_TS] = sps[3].get_text().strip()
        links.append(info)

    # 找到所有目录后面页地址
    pager = bs.find("div", attrs={"class": "page"})
    current_page = re.findall(u"([\d]+)$", pre_information[URL])
    current_page = int(current_page[0])
    total_page = re.findall(u'共([\d]+)页', pager.get_text())
    total_page = int(total_page[0])

    def next_page_func(info, next_page):
        info[URL] = re.sub("\d+$", "%s" % next_page, info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.sjzjzsc.com/ZBGS_D.ASPX?ID=%s", "\d+"))
def hb_zfcgw_nr(html, pre_information):
    links, contents = [], []

    # html = html_purify(html)
    selector = build_etree_xpath(html.decode("utf-8"))
    content_node = selector.xpath('//*[@id="Table1"]')[0]
    content = etree.tounicode(content_node)

    sums = {}
    content = build_beautiful_soup(content)
    tds = content.find_all("td")
    for idx in range(0, len(tds) - 1, 2):
        k = tds[idx].get_text().strip().strip(u"：:")
        v = tds[idx + 1].get_text().strip()
        sums[k] = v
        if k == u"中标价" and re.match(u"^(?:\d+|\d+\.\d+)$", v):
            tds[idx + 1].string = v + u"万元"

    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        info[CONTENT] = str(html_purify(content))
    info[CONTENT] = str(content)

    if u"工程名称" in sums:
        info[PROJECT_NAME] = sums.pop(u"工程名称")
    if u"建设单位" in sums:
        info[PURCHASER_NAME] = sums.pop(u"建设单位")
    if u"招标方式" in sums:
        info[PURCHASE_TYPE] = sums.pop(u"招标方式")
    if u"代理单位" in sums:
        info[AGENT_NAME] = sums.pop(u"代理单位")
    if u"中标结果公示日期" in sums:
        t = sums.pop(u"中标结果公示日期")
        if t:
            info[PUBLISHED_TS] = t
    info[OTHERS] = sums

    contents.append(info)

    return links, contents


# 邢台市政务服务中心
@add_url(url_filter("http://zyjy.xtsxzfw.gov.cn:83/web/list1.aspx"))
def hb_xtszwfwzx_ml(html, pre_information):
    links, contents = [], []

    host = "http://zyjy.xtsxzfw.gov.cn:83/web/"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    ttl = bs.find_all("td", attrs={"height": "26", "class": "list_tb"})
    tsl = bs.find_all("td", attrs={"height": "26", "class": "rq",
                                   "style": "text-align: right;font-size:18px", "nowrap": ""})
    lst = zip(ttl, tsl)
    for item in lst:
        info = copy.deepcopy(pre_information)
        t = item[0].find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t.get_text().strip()
        info[PUBLISHED_TS] = extract_first_date(item[1].get_text())
        links.append(info)

    # 找到所有目录后面页地址
    current_page = bs.find("span", id="spaCurrentPage").get_text().strip()
    current_page = int(current_page)
    total_page = bs.find("span", id="spaRecordCount").get_text().strip()
    total_page = int(total_page)

    def next_page_func(info, next_page):
        info[URL] = re.sub("Page=\d+", "Page=%s" % next_page, info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://zyjy.xtsxzfw.gov.cn:83/web/info1.aspx"))
def hb_xtszwfwzx_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("span", id="spaContent")
    ts = bs.find("span", id="spaCreatedAt")

    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        info[CONTENT] = str(html_purify(content))
    info[CONTENT] = str(content)

    ts = extract_first_date(ts.get_text())
    if ts:
        info[PUBLISHED_TS] = ts

    contents.append(info)

    return links, contents


# 邢台建设信息网
# TODO ....
@add_url(url_filter("http://www.xtjsj.gov.cn/bsinfolist.asp"))
def hb_xtjsxxw_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.xtjsj.gov.cn/"
    # 找到所有列表项目地址
    selector = build_etree_xpath(html.decode("utf-8"))
    lst = selector.xpath('//*[@id="div2_1"]/table/tbody/tr/td/table[1]/tr')
    for item in lst:
        t = item.xpath("td/span/a")
        if not t:
            continue
        info = copy.deepcopy(pre_information)
        info[URL] = host + item.xpath(".//a/@href")[0]
        info[TITLE] = item.xpath(".//a/text()")[0].strip()
        txt = item.xpath('.//span[@class="addTime"]/text()')[0]
        info[PUBLISHED_TS] = extract_first_date(txt)
        links.append(info)

    # 找到所有目录后面页地址
    bs = build_beautiful_soup(html)
    pager = bs.find("table", attrs={"width": "98%", "border": "0", "cellspacing": "0", "cellpadding": "0"})
    current_page, total_page = re.findall(u"(\d+)/(\d+)", pager.get_text())[0]
    current_page = int(current_page)
    total_page = int(total_page)

    def next_page_func(info, next_page):
        info[URL] = re.sub("Page=\d+", "Page=%s" % next_page, info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.xtjsj.gov.cn/bsinfoshow.Asp"))
def hb_xtjsxxw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", id="div2_1")

    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        info[CONTENT] = str(html_purify(content))
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================河  北================ #
# =================END================= #


# ================START================ #
# ================上  海================ #
# TODO


# ================上  海================ #
# =================END================= #


# ================START================ #
# ================重  庆================ #

# 重庆市政府采购网
@add_url(url_filter("https://www.cqgp.gov.cn/gwebsite/api/v1/notices/stable?pi="))
def cq_szfcgw_ml(html, pre_information):
    links, contents = [], []

    # 找到所有列表项目地址
    host = "https://www.cqgp.gov.cn/notices/detail/"
    host_ = "https://www.cqgp.gov.cn/gwebsite/api/v1/notices/stable/"
    project_purchase_way = {"100": u"公开招标", "200": u"邀请招标", "300": u"竞争性谈判", "400": u"询价", "500": u"单一来源",
                            "800": u"竞争性磋商", "6001": u"电子竞价", "6002": u"电子反拍"}
    notice_type = {"300": u"成交公告", "302": u"结果公告", "304": u"废标公告", "305": u"流标公告"}
    data = json.loads(html)
    lst = data.get("notices")
    for item in lst:
        info = copy.deepcopy(pre_information)
        info[URL] = host + item["id"]
        info[DATA_URL] = host_ + item["id"]
        info[TITLE] = item["title"]
        info[PUBLISHED_TS] = extract_first_date(item["issueTime"], is_str=True)
        if "districtName" in item:
            info[REGION] = u"重庆>>" + item.get("districtName")
        if "noticeType" in item:
            info[ANNOUNCE_TYPE] = notice_type.get(str(item["noticeType"]))
        if "projectPurchaseWay" in item:
            info[PURCHASE_TYPE] = project_purchase_way.get(str(item["projectPurchaseWay"]))
        if "projectBudget" in item:
            info[PROJECT_BUDGET] = item.get("projectBudget")
        info[PROJECT_CONTACT_NAME] = item.get("creatorOrgName")
        info[PURCHASE_CATEGORY] = item.get("projectDirectoryName")
        info[PURCHASER_NAME] = item.get("buyerName")
        info[AGENT_NAME] = item.get("agentName")
        info[OPEN_BID_TS] = item.get("openBidTime")
        info[END_BID_TS] = item.get("bidEndTime")
        links.append(info)

    # 找到所有目录后面页地址
    current_page = re.findall("pi=\d+", pre_information[URL])[0][3:]
    current_page = int(current_page)
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    page_size = re.findall("ps=\d+", pre_information[URL])[0][3:]
    page_size = int(page_size)
    total_page = math.ceil(float(data.get("total")) / page_size)

    while current_page < total_page:
        next_page_info = copy.deepcopy(pre_information)
        next_page_info[URL] = re.sub("pi=\d+", "pi=%s" % (current_page + 1), next_page_info[URL])
        if pre_information.get(GENERATE_ALL_PAGE):  # 判断是否直接生成后面所有目录页地址
            next_page_info[GENERATED_PAGE] = total_page
            links.append(next_page_info)
            current_page += 1
        else:
            links.append(next_page_info)
            break

    return links, contents


@add_url(url_filter("https://www.cqgp.gov.cn/gwebsite/api/v1/notices/stable/%s", "\d+"))
def cq_szfcgw_nr(html, pre_information):
    links, contents = [], []

    data = json.loads(html)
    notice = data.get("notice", {})
    content = notice.get("html")
    category = notice.get("projectDirectoryName")
    budget = notice.get("projectBudget", "")
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)
    info[PURCHASE_CATEGORY] = category
    t = re.findall(u"\d+(?:.\d+)?", str(budget))
    if len(t) > 0:
        info[PROJECT_BUDGET] = float(t[0])
    if "projectPurchaseWayName" in notice:
        info[PURCHASE_TYPE] = notice.get("projectPurchaseWayName")
    contents.append(info)

    return links, contents


# 重庆市招标投标综合网
@add_url(url_filter("http://www.cqzb.gov.cn/class-5-45(%s).aspx", "\d+"))
def cq_zbtbw_ml(html, pre_information):
    links, contents = [], []

    # 找到所有列表项目地址
    host = "http://www.cqzb.gov.cn/"
    bs = build_beautiful_soup(html)
    lst = bs.find("div", attrs={"class": "ztb_list_right"}).find("ul").find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        t = item.find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t.get_text().strip()
        info[PUBLISHED_TS] = extract_first_date(item.find("span").get_text(), is_str=True)
        links.append(info)

    # 找到所有目录后面页地址
    current_page = re.findall("\(\d+\)", pre_information[URL])[0][1:-1]
    current_page = int(current_page)
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    pager = bs.find("div", attrs={"class": "pages"})
    total_page = re.findall("/\d+", pager.get_text())[0][1:]
    total_page = int(total_page)

    while current_page < total_page:
        next_page_info = copy.deepcopy(pre_information)
        next_page_info[URL] = re.sub("\(\d+\)", "(%s)" % (current_page + 1), next_page_info[URL])
        if pre_information.get(GENERATE_ALL_PAGE):  # 判断是否直接生成后面所有目录页地址
            next_page_info[GENERATED_PAGE] = total_page
            links.append(next_page_info)
            current_page += 1
        else:
            links.append(next_page_info)
            break

    return links, contents


@add_url(url_filter("http://www.cqzb.gov.cn/zbgg"))
def cq_zbtbw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("table", attrs={"class": "MsoNormalTable"})
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# 重庆各个区县公共资源交易中心
# 重庆市公共资源交易中心
@add_url(url_filter("http://www.cqggzy.com/web/services/PortalsWebservice/getInfoList"))
def cq_ggzyjyzx_ml(html, pre_information):
    links, contents = [], []

    # 找到所有列表项目地址
    host = "http://www.cqggzy.com"
    data = json.loads(html, strict=False)
    lst = json.loads(data["return"], strict=False)
    for item in lst:
        info = copy.deepcopy(pre_information)
        info[URL] = host + item["infourl"]
        info[TITLE] = item["title"]
        info[PUBLISHED_TS] = extract_first_date(item["infodate"], is_str=True)
        info[REGION] = u"重庆>>" + item["infoC"]
        links.append(info)

    # 找到所有目录后面页地址
    current_page = re.findall("(?<=pageIndex\=)\d+", pre_information[URL])
    if len(current_page) == 0:
        current_page = 1
    else:
        current_page = int(current_page[0])

    total_page = current_page
    if len(lst) > 0:
        total_page = current_page + 1

    def next_page_func(info, next_page):
        info[URL] = re.sub("pageIndex\=\d+", "pageIndex=%s" % next_page, info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.cqggzy.com/xxhz"))
def cq_ggzyjyzx_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", id="mainContent")
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


@add_url(url_filter("http://www.wzqztb.com/wzweb/jyxx/001001/001001005/MoreInfo.aspx?CategoryNum=001001005"))
@add_url(url_filter("http://www.ybggb.com.cn/cqybwz/jyxx/001001/001001005/MoreInfo.aspx?CategoryNum=262661"))
@add_url(url_filter("http://jyzx.beibei.gov.cn/cqbbwz/002/002001/002001004/MoreInfo.aspx?CategoryNum=002001004"))
@add_url(url_filter("http://www.cqyzbid.com/cqyzwz/jyxx/003001/003001004/MoreInfo.aspx?CategoryNum=003001004"))
@add_url(url_filter("http://www.cqjlpggzyzhjy.gov.cn/cqjl/jyxx/003001/003001002/MoreInfo.aspx?CategoryNum=003001002"))
def cq_cqyzbid_ml(html, pre_information):
    links, contents = [], []

    try:
        selector = build_etree_xpath(html.decode('utf8'))
    except:
        selector = build_etree_xpath(html.decode('gbk'))

    __VIEWSTATE = selector.xpath("//input[contains(@id, '__VIEWSTATE')]/@value")[0]
    __EVENTTARGET = 'MoreInfoList1$Pager'

    current_page = pre_information.get(PARAMS, {}).get("__EVENTARGUMENT", 0)
    total_page = selector.xpath("//*[@id=\"MoreInfoList1_Pager\"]/table/tr/td[1]/font[2]/b/text()")[0]
    total_page = int(total_page)
    if 'cqyzbid' in pre_information[URL]:
        host = "http://www.cqyzbid.com"
        __CSRFTOKEN = selector.xpath("//input[contains(@id, '__CSRFTOKEN')]/@value")[0]
    elif 'beibei' in pre_information[URL]:
        host = 'http://jyzx.beibei.gov.cn'
        __CSRFTOKEN = selector.xpath("//input[contains(@id, '__CSRFTOKEN')]/@value")[0]
        __VIEWSTATEGENERATOR = selector.xpath("//input[contains(@id, '__VIEWSTATEGENERATOR')]/@value")[0]
    elif 'cqjlpggzyzhjy' in pre_information[URL]:
        host = 'http://www.cqjlpggzyzhjy.gov.cn'
        __CSRFTOKEN = ''
    elif 'ybggb' in pre_information[URL]:
        host = "http://www.ybggb.com.cn"
        __VIEWSTATEGENERATOR = selector.xpath("//input[contains(@id, '__VIEWSTATEGENERATOR')]/@value")[0]
    elif 'wzqztb' in pre_information[URL]:
        host = 'http://www.wzqztb.com'

    print "第 %s/%s 页" % (current_page, total_page)

    def next_page_func(info, next_page):
        info[METHOD] = POST
        if 'cqyz' in info[URL]:
            info[PARAMS] = dict(__CSRFTOKEN=__CSRFTOKEN, __VIEWSTATE=__VIEWSTATE,
                                __EVENTTARGET=__EVENTTARGET, __EVENTARGUMENT=next_page)
        elif 'beibei' in info[URL]:
            info[PARAMS] = dict(__CSRFTOKEN=__CSRFTOKEN, __VIEWSTATE=__VIEWSTATE,
                                __VIEWSTATEGENERATOR=__VIEWSTATEGENERATOR,
                                __EVENTTARGET=__EVENTTARGET, __EVENTARGUMENT=next_page)
        elif 'cqjlp' in info[URL]:
            info[PARAMS] = dict(__VIEWSTATE=__VIEWSTATE,
                                __EVENTTARGET=__EVENTTARGET, __EVENTARGUMENT=next_page)
        elif 'ybggb' in info[URL]:
            info[PARAMS] = dict(__VIEWSTATE=__VIEWSTATE, __VIEWSTATEGENERATOR=__VIEWSTATEGENERATOR,
                                __EVENTTARGET=__EVENTTARGET, __EVENTARGUMENT=next_page)
        elif 'wzqztb' in info[URL]:
            info[PARAMS] = dict(__VIEWSTATE=__VIEWSTATE, __EVENTTARGET=__EVENTTARGET,
                                __EVENTARGUMENT=next_page)

    links += next_pages(pre_information, next_page_func, current_page, total_page)
    item_list = selector.xpath("//table[contains(@id, 'MoreInfoList1_DataGrid1')]/tr")

    for item in item_list:
        info = copy.deepcopy(pre_information)
        info[URL] = host + item.xpath("./td/a/@href")[0].strip()
        if item.xpath("./td/a/font/text()"):
            info[TITLE] = item.xpath("./td/a/font/text()")[0].strip()
        else:
            info[TITLE] = item.xpath("./td/a/text()")[0].strip()
        info[METHOD] = GET
        info[PUBLISHED_TS] = extract_first_date(item.xpath("./td[last()]/text()")[0].strip(), is_str=True)
        links.append(info)

    return links, contents


@add_url(url_filter("http://www.wzqztb.com/wzweb/InfoDetail/Default.aspx?InfoID="))
@add_url(url_filter("http://www.ybggb.com.cn/cqybwz/InfoDetail/Default.aspx?InfoID="))
@add_url(url_filter("http://jyzx.beibei.gov.cn/cqbbwz/InfoDetail/Default.aspx?InfoID="))
@add_url(url_filter("http://www.cqyzbid.com/cqyzwz/InfoDetail/Default.aspx?InfoID="))
@add_url(url_filter("http://www.cqjlpggzyzhjy.gov.cn/cqjl/InfoDetail/Default.aspx?InfoID="))
def cq_cqyzbid_nr(html, pre_information):
    links, contents = [], []
    # print pre_information[TITLE]
    # print pre_information[URL]
    info = copy.deepcopy(pre_information)
    try:
        selector = build_etree_xpath(html.decode('utf8'))
    except:
        selector = build_etree_xpath(html.decode('gbk'))
    # try:
    if selector.xpath("//td[contains(@id, 'TDContent')]"):
        content_node = selector.xpath("//td[contains(@id, 'TDContent')]")[0]
    else:
        content_node = selector.xpath("//div[contains(@class, 'p-content')]")[0]
    content = etree.tounicode(content_node)
    # except Exception as e:
    #     import traceback
    #     traceback.print_exc(e)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = content
    contents.append(info)
    return links, contents


@add_url(url_filter('http://jy.bnzw.gov.cn/LBv3/n_newslist_zz.aspx?Item=100026'))
def cq_bnzw_ml(html, pre_info):
    links, contents = [], []
    root_url = 'http://jy.bnzw.gov.cn/LBv3/'
    selector = build_etree_xpath(html)
    url_list = set(selector.xpath("//td/a[contains(@href, 'n_newslist_zb')]/@href"))
    for url in url_list:
        info = copy.deepcopy(pre_info)
        info[URL] = root_url + url.replace("n_newslist_zb.aspx", "n_newslist_zb_item.aspx")
        links.append(info)
    return links, contents


@add_url(url_filter('http://jy.bnzw.gov.cn/LBv3/n_newslist_zb.aspx?Item=2'))
@add_url(url_filter('http://jy.bnzw.gov.cn/LBv3/n_newslist_zb_item.aspx?Item=2'))
@add_url(url_filter('http://www.flzbjy.com/lbWeb/n_newslist_item.aspx?Item=200010'))
@add_url(url_filter('http://www.ckjyzx.cn/LBv3/n_newslist_zz_item.aspx?Item=200010'))
@add_url(url_filter('http://www.qjdtc.com/LBv3/n_newslist_zz_item.aspx?Item=200010'))
@add_url(url_filter('http://www.tljyzx.com/lbv3/n_newslist_zz_item.aspx?Item=200010'))
@add_url(url_filter('http://www.cqtnjy.com/lbv3/n_newslist_zz_item.aspx?Item=200010'))
@add_url(url_filter('http://www.fdggzy.cn/lbWeb/n_newslist_zz_item.aspx?ILWHBNjF4clKo8UY2fiQHA='))
@add_url(url_filter('http://www.zxggzy.cn/lbWeb/n_newslist_zz_item.aspx?Item=200010'))
@add_url(url_filter('http://www.yyggzy.com/lbWeb/n_newslist_zz_item.aspx?Item=200010'))
@add_url(url_filter('http://www.xsggzy.com/lbv3/n_newslist_zz_item.aspx?ILWHBNjF4clKo8UY2fiQHA'))
@add_url(url_filter("http://www.cqqjxjy.com/LBv3/n_newslist_zz_item.aspx"))
@add_url(url_filter('http://www.fjjyzx.net/lbWeb/n_newslist_zz_item.aspx?Item=200010'))
@add_url(url_filter('http://www.cqhcjy.com/lbWeb/n_newslist_zz_item.aspx?ILWHBNjF4clKo8UY2fiQHA='))
@add_url(url_filter("http://www.ncggjy.com/lbWeb/n_newslist_zz_item.aspx?Item=200010"))
@add_url(url_filter("http://www.ddkggzy.com/lbv3/n_newslist_zz_item.aspx"))
@add_url(url_filter("http://www.ddkggzy.com/lbWeb/n_newslist_zz_item.aspx?ILWHBNjF4clKo8UY2fiQHA"))
@add_url(url_filter('http://www.023sqjy.com/lbWeb/n_newslist_zz_item.aspx?Item=200010'))
@add_url(url_filter('http://www.cqspbjyzx.com/LBv3/n_newslist_zz_item.aspx?Item=200010'))
@add_url(url_filter('http://www.cqspbjyzx.com/LBv3/n_newslist_zz_item.aspx?ILWHBNjF4clKo8UY2fiQHA=='))
@add_url(url_filter('http://www.cqdzjyzx.com/lbWeb/n_newslist_zz_item.aspx?Item=200010'))
@add_url(url_filter('http://www.wsggzyjy.com/lbWeb/n_newslist_zz_item.aspx?ILWHBNjF4clKo8UY2fiQHA='))
@add_url(url_filter('http://www.cqszggzyjy.com/lbv3/n_newslist_zz_item.aspx?Item=200010'))
@add_url(url_filter('http://www.cqszggzyjy.com/lbv3/n_newslist_zz_item.aspx%sCrZgb12k3hKo8UY2fiQHA==', "[\?\+]+"))
@add_url(url_filter('http://www.djjyzx.gov.cn/lbweb/n_newslist_zz_item.aspx?Item=200010'))
@add_url(url_filter('http://www.cqjbjyzx.gov.cn/lbWeb/n_newslist_zz_item.aspx?Item=200010'))
@add_url(url_filter('http://www.cqjbjyzx.gov.cn/lbWeb/n_newslist_zz_item.aspx?ILWHBNjF4clKo8UY2fiQHA=='))
def cq_cqqjxjy_ml(html, pre_information):
    links, contents = [], []

    if 'cqqj' in pre_information[URL]:
        root_url = "http://www.cqqjxjy.com/LBv3/"
        selector = etree.HTML(html.decode('utf8'))
    elif 'ddk' in pre_information[URL]:
        root_url = 'http://www.ddkggzy.com/lbv3/'
        selector = etree.HTML(html.decode('utf8'))
    elif 'cqjbjyzx' in pre_information[URL]:
        root_url = 'http://www.cqjbjyzx.gov.cn/lbWeb/'
        selector = etree.HTML(html.decode('utf8'))
    elif 'cqspb' in pre_information[URL]:
        root_url = 'http://www.cqspbjyzx.com/LBv3/'
        selector = etree.HTML(html)
    elif '023sqjy' in pre_information[URL]:
        root_url = 'http://www.023sqjy.com/lbWeb/'
        selector = etree.HTML(html.decode('gbk'))
    elif 'yyggzy' in pre_information[URL]:
        root_url = 'http://www.yyggzy.com/lbWeb/'
        selector = etree.HTML(html)
    elif 'xsggzy' in pre_information[URL]:
        root_url = 'http://www.xsggzy.com/lbv3/'
        selector = etree.HTML(html.decode('utf8'))
    elif 'cqszggzyjy' in pre_information[URL]:
        root_url = 'http://www.cqszggzyjy.com/lbv3/'
        selector = etree.HTML(html.decode('utf8'))
    elif 'wsggzyjy' in pre_information[URL]:
        root_url = 'http://www.wsggzyjy.com/lbWeb/'
        selector = etree.HTML(html.decode('utf8'))
    elif 'fjjyzx' in pre_information[URL]:
        import chardet
        code = chardet.detect(html).get("encoding", "gbk")
        root_url = 'http://www.fjjyzx.net/lbWeb/'
        if code.lower() in ("gbk", "gb2312"):
            selector = etree.HTML(html.decode('gbk'))
        else:
            selector = etree.HTML(html.decode('utf-8'))
    elif 'jy.bnzw' in pre_information[URL]:
        root_url = 'http://jy.bnzw.gov.cn/LBv3/'
        selector = etree.HTML(html)
    elif 'flzbjy' in pre_information[URL]:
        root_url = 'http://www.flzbjy.com/lbWeb/'
        selector = etree.HTML(html)
    elif 'qjdtc' in pre_information[URL]:
        root_url = 'http://www.qjdtc.com/LBv3/'
        selector = etree.HTML(html.decode('utf8'))
    elif 'cqhcjy' in pre_information[URL]:
        root_url = 'http://www.cqhcjy.com/lbWeb/'
        selector = etree.HTML(html)
    elif 'ncggjy' in pre_information[URL]:
        root_url = 'http://www.ncggjy.com/lbWeb/'
        selector = etree.HTML(html)
    elif 'cqtnjy' in pre_information[URL]:
        root_url = 'http://www.cqtnjy.com/lbv3/'
        selector = etree.HTML(html.decode('utf8'))
    elif 'tljyzx' in pre_information[URL]:
        root_url = 'http://www.tljyzx.com/lbv3/'
        selector = etree.HTML(html.decode('utf8'))
    elif 'cqdzjyzx' in pre_information[URL]:
        root_url = 'http://www.cqdzjyzx.com/lbWeb/'
        selector = etree.HTML(html)
    elif 'ckjyzx' in pre_information[URL]:
        root_url = 'http://www.ckjyzx.cn/LBv3/'
        selector = etree.HTML(html.decode('utf8'))
    elif 'fdggzy' in pre_information[URL]:
        root_url = 'http://www.fdggzy.cn/lbWeb/'
        selector = etree.HTML(html)
    elif 'djjyzx' in pre_information[URL]:
        root_url = 'http://www.djjyzx.gov.cn/lbweb/'
        selector = etree.HTML(html.decode('gbk'))
    elif 'zxggzy' in pre_information[URL]:
        root_url = 'http://www.zxggzy.cn/lbWeb/'
        selector = etree.HTML(html.decode('gbk'))

    post_data = {
        '__VIEWSTATE': selector.xpath("//input[contains(@id, '__VIEWSTATE')]/@value")[0],
        '__EVENTVALIDATION': selector.xpath("//input[contains(@id, '__EVENTVALIDATION')]/@value")[0],
        'ctl00$ContentPlaceHolder2$F3': '下一页',
    }
    if selector.xpath("//td/span[contains(@id, 'ctl00_ContentPlaceHolder2_A2')]/text()"):
        current_page = selector.xpath("//td/span[contains(@id, 'ctl00_ContentPlaceHolder2_A2')]/text()")[0]
    elif selector.xpath("//td/input[contains(@id, 'ctl00_ContentPlaceHolder2_T2')]/@value"):
        current_page = selector.xpath("//td/input[contains(@id, 'ctl00_ContentPlaceHolder2_T2')]/@value")[0]
        post_data['ctl00_ContentPlaceHolder2_T2'] = current_page
    else:
        current_page = selector.xpath("//td/span[contains(@id, 'ctl00_ContentPlaceHolder2_A2')]/font/text()")[0]

    if selector.xpath("//td/span[contains(@id, 'ctl00_ContentPlaceHolder2_A1')]/text()"):
        total_page = selector.xpath("//td/span[contains(@id, 'ctl00_ContentPlaceHolder2_A1')]/text()")[0]
    elif selector.xpath("//td/input[contains(@id, 'ctl00_ContentPlaceHolder2_T1')]/@value"):
        total_page = selector.xpath("//td/input[contains(@id, 'ctl00_ContentPlaceHolder2_T1')]/@value")[0]
        post_data['ctl00_ContentPlaceHolder2_T1'] = total_page
    else:
        total_page = selector.xpath("//td/span[contains(@id, 'ctl00_ContentPlaceHolder2_A1')]/font/text()")[0]
    current_page = int(current_page)
    total_page = int(total_page)
    print "处理[%s/%s]" % (current_page, total_page)

    def next_page_func(info, next_page):
        info[METHOD] = POST
        info[PARAMS] = post_data

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    item_list = selector.xpath("//table[contains(@id, 'ctl00_ContentPlaceHolder2_DataList1')]/tr")
    for item in item_list:
        info = copy.deepcopy(pre_information)
        info[METHOD] = GET
        info[URL] = root_url + item.xpath("./td[1]/table/tr/td/nobr/a/@href")[0]
        info[TITLE] = item.xpath("./td[1]/table/tr/td/nobr/a/text()")[0]
        if 'cqjb' in root_url:
            info[PUBLISHED_TS] = extract_first_date(item.xpath("./td[1]/table/tr/td/nobr/span/text()")[0])
        else:
            info[PUBLISHED_TS] = extract_first_date(item.xpath("./td[1]/table/tr/td/nobr/text()")[0])
        links.append(info)
    return links, contents


@add_url(url_filter("http://www.bsggjy.com/n_newsdetail_zz.aspx?"))
@add_url(url_filter("http://www.flzbjy.com/lbWeb/n_newsdetail.aspx"))
@add_url(url_filter("http://www.qjdtc.com/LBv3/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.ckjyzx.cn/LBv3/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://jy.bnzw.gov.cn/LBv3/n_newsdetail_zb.aspx"))
@add_url(url_filter("http://www.tljyzx.com/lbv3/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.fdggzy.cn/lbWeb/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.cqtnjy.com/lbv3/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.zxggzy.cn/lbWeb/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.cqhcjy.com/lbWeb/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.cqqjxjy.com/LBv3/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.yyggzy.com/lbWeb/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.xsggzy.com/lbv3/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.fjjyzx.net/lbWeb/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.ncggjy.com/lbWeb/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.ddkggzy.com/lbWeb/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.ddkggzy.com/lbv3/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.023sqjy.com/lbWeb/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.wsggzyjy.com/lbWeb/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.cqspbjyzx.com/LBv3/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.cqdzjyzx.com/lbWeb/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.cqszggzyjy.com/lbv3/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.djjyzx.gov.cn/lbweb/n_newsdetail_zz.aspx"))
@add_url(url_filter("http://www.cqjbjyzx.gov.cn/lbWeb/n_newsdetail_zz.aspx"))
def cq_cqqjxjy_nr(html, pre_info):
    # print pre_info
    links, contents = [], []
    info = copy.deepcopy(pre_info)
    root_url = ""
    if 'cqqj' in pre_info[URL]:
        root_url = 'http://www.cqqjxjy.com/'
        selector = etree.HTML(html.decode('utf8'))
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif 'ddk' in pre_info[URL]:
        root_url = 'http://www.ddkggzy.com/'
        selector = etree.HTML(html.decode('utf8'))
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[1])
    elif 'cqjb' in pre_info[URL]:
        root_url = 'http://www.cqjbjyzx.gov.cn/'
        selector = etree.HTML(html.decode('utf8'))
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif '023sqjy' in pre_info[URL]:
        root_url = 'http://www.023sqjy.com/'
        selector = etree.HTML(html.decode('gbk'))
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif 'cqspb' in pre_info[URL]:
        root_url = 'http://www.cqspbjyzx.com/'
        selector = etree.HTML(html)
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif 'yyggzy' in pre_info[URL]:
        root_url = 'http://www.yyggzy.com/'
        selector = etree.HTML(html)
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif 'xsggzy' in pre_info[URL]:
        root_url = 'http://www.xsggzy.com/'
        selector = etree.HTML(html.decode('utf8'))
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif 'cqszggzyjy' in pre_info[URL]:
        root_url = 'http://www.cqszggzyjy.com/'
        selector = etree.HTML(html.decode("utf8"))
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif 'wsggzyjy' in pre_info[URL]:
        root_url = 'http://www.wsggzyjy.com/'
        selector = etree.HTML(html.decode('utf-8'))
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif 'fjjyzx' in pre_info[URL]:
        import chardet
        code = chardet.detect(html).get("encoding", "gbk")
        root_url = 'http://www.fjjyzx.net/'
        if code.lower() in ("gbk", "gb2312"):
            selector = etree.HTML(html.decode('gbk'))
        else:
            selector = etree.HTML(html.decode('utf-8'))
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif 'jy.bnzw' in pre_info[URL]:
        root_url = 'http://jy.bnzw.gov.cn/'
        selector = etree.HTML(html)
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif 'flzbjy' in pre_info[URL]:
        root_url = 'http://www.flzbjy.com/'
        selector = etree.HTML(html)
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif 'qjdtc' in pre_info[URL]:
        root_url = 'http://www.qjdtc.com/'
        selector = build_etree_xpath(html.decode('utf8'))
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif 'cqhcjy' in pre_info[URL]:
        root_url = 'http://www.cqhcjy.com/'
        selector = build_etree_xpath(html)
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif 'ncggjy' in pre_info[URL]:
        root_url = 'http://www.ncggjy.com/'
        selector = build_etree_xpath(html)
        content = etree.tounicode(selector.xpath("//td[@width='88%']")[0])
    elif 'cqtnjy' in pre_info[URL]:
        root_url = 'http://www.cqtnjy.com/'
        selector = build_etree_xpath(html.decode('utf8'))
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif 'tljyzx' in pre_info[URL]:
        root_url = 'www.tljyzx.com'
        selector = etree.HTML(html.decode('utf8'))
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif 'cqdzjyzx' in pre_info[URL]:
        root_url = 'www.cqdzjyzx.com'
        selector = etree.HTML(html)
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif 'bsggjy' in pre_info[URL]:
        root_url = 'www.bsggjy.com'
        selector = etree.HTML(html)
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif 'ckjyzx' in pre_info[URL]:
        selector = etree.HTML(html.decode('utf8'))
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
        root_url = 'http://www.ckjyzx.cn.com'
    elif 'fdggzy' in pre_info[URL]:
        selector = etree.HTML(html)
        root_url = 'http://www.fdggzy.cn'
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif 'djjyzx' in pre_info[URL]:
        selector = etree.HTML(html.decode('gbk'))
        root_url = 'http://www.djjyzx.gov.cn'
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])
    elif 'zxggzy' in pre_info[URL]:
        selector = etree.HTML(html.decode('gbk'))
        root_url = 'http://www.zxggzy.cn'
        content = etree.tounicode(selector.xpath("//td[@width='96%']")[0])

    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = content
    if len(content) < 300 and '<img' in content:
        print "发现图片", info[URL]
        img_url = re.findall('src="(\S+)"', content)[0]
        if 'http' not in img_url:
            if root_url.endswith("/") and img_url.startswith("/"):
                root_url = root_url[:-1]
            elif not root_url.endswith("/") and not img_url.startswith("/"):
                root_url += "/"
            img_url = root_url + img_url
        import requests, base64
        img_src = base64.b64encode(requests.get(img_url).content)
        info[APPENDIX] = [{
            "scr_url": img_url,
            "src_data": img_src,
            'type': 'img',
        }]
    contents.append(info)
    return links, contents


@add_url(url_filter('http://www.bsggjy.com/n_newslist_zz_item.aspx?Item=200010'))
def cq_bsggjy_ml(html, pre_info):
    links, contents = [], []
    root_url = 'http://www.bsggjy.com/'
    selector = build_etree_xpath(html)
    # current_page = selector.xpath("//input[contains(@id, 'ContentPlaceHolder2_T2')]/@value")[0]
    total_page = selector.xpath("//input[contains(@id, 'ContentPlaceHolder2_T1')]/@value")[0]
    current_page = pre_info.get(PARAMS, {}).get('ctl00$ContentPlaceHolder2$T2', 0)
    total_page = int(total_page)
    post_data = {
        '__VIEWSTATE': selector.xpath("//input[contains(@id, '__VIEWSTATE')]/@value")[0],
        '__EVENTVALIDATION': selector.xpath("//input[contains(@id, '__EVENTVALIDATION')]/@value")[0],
        'ctl00$ContentPlaceHolder2$F3': '下一页',
        'ctl00$ContentPlaceHolder2$T1': str(total_page),
    }
    print "处理[%s/%s]" % (current_page, total_page)

    def next_page_func(info, next_page):
        info[METHOD] = POST
        info[PARAMS] = post_data
        info[PARAMS]['ctl00$ContentPlaceHolder2$T2'] = next_page

    links += next_pages(pre_info, next_page_func, current_page, total_page)

    item_list = selector.xpath("//table[contains(@id, 'ContentPlaceHolder2_DataList1')]/tr")
    for item in item_list:
        info = copy.deepcopy(pre_info)
        info[METHOD] = GET
        info[TITLE] = item.xpath("./td/table/tr/td[nobr[a]]/nobr/a/text()")[0]
        info[URL] = root_url + item.xpath("./td/table/tr/td[nobr[a]]/nobr/a/@href")[0]
        info[PUBLISHED_TS] = extract_first_date(item.xpath("./td/table/tr/td[nobr[text()]]/nobr/text()")[0])
        links.append(info)
    return links, contents


@add_url(url_filter("http://zyjy.rongchang.gov.cn/WEB/PageTradingCenter/index_list.jsp?pageId=360403"))
def cq_rongchang_index(html, pre_info):
    links, contents = [], []
    info = copy.deepcopy(pre_info)
    info[URL] = 'http://zyjy.rongchang.gov.cn/WEB/template/parse/pagingAction.do?' \
                'method=getPageData&moduleId=PM_20141014002&page=1&timestamp=%s' % str(int(time.time() * 1000))
    links.append(info)
    return links, contents


@add_url(url_filter("http://zyjy.rongchang.gov.cn/WEB/template/parse/pagingAction.do"))
def cq_rongchang_ml(html, pre_info):
    links, contents = [], []
    res_json = json.loads(html)
    html = res_json.get("message")
    selector = build_etree_xpath(html)
    total_page = selector.xpath("//select/option[last()]/text()")[0]
    total_page = int(re.findall('\d+', total_page)[0])
    current_page = selector.xpath(u"//span[contains(@title, '当前页')]/b/text()")[0]
    current_page = int(re.findall('\d+', current_page)[0])
    print "[%s/%s]" % (current_page, total_page)

    def next_page_func(info, next_page):
        info[URL] = 'http://zyjy.rongchang.gov.cn/WEB/template/parse/pagingAction.do?method=getPageData' \
                    '&moduleId=PM_20141014002&page=%s&timestamp=%s' % (next_page, str(int(time.time() * 1000)))

    links += next_pages(pre_info, next_page_func, current_page, total_page)
    item_list = selector.xpath("//a[span]")
    for item in item_list:
        info = copy.deepcopy(pre_info)
        info[TITLE] = item.xpath("./text()")[0].strip()
        info[URL] = "http://zyjy.rongchang.gov.cn" + item.xpath("./@href")[0].strip()
        info[PUBLISHED_TS] = extract_first_date(item.xpath("./span/text()")[0].strip('[]').strip())
        links.append(info)
    return links, contents


@add_url(url_filter("http://zyjy.rongchang.gov.cn/WEB/PageTradingCenter/details.jsp?infoid="))
def cq_rongchang_nr(html, pre_info):
    links, contents = [], []
    info = copy.deepcopy(pre_info)
    selector = build_etree_xpath(html)
    content = etree.tounicode(selector.xpath("//table[contains(@class, 'h22')]")[0])
    info[CONTENT] = content
    contents.append(info)
    return links, contents


@add_url(url_filter("http://www.wlzyzx.cn/ceinwz/msjyjggs.aspx?xmlx=10&FromUrl=msjyjggs.htm&zbdl=1"))
@add_url(url_filter("http://www.cqkxjyzx.com/ceinwz/msjyjggs.aspx?xmlx=10&FromUrl=msjyjggs.htm&zbdl=1&newsid=0"))
@add_url(url_filter(
    "http://www.csggzyjy.com/ceinwz/WebInfo_List.aspx?newsid=5000&jsgc=00000010&zfcg=&tdjy=&cqjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=1&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=jsgc"))
@add_url(url_filter("http://www.cqlpjyzx.com/ceinwz/webInfo_List.aspx?"))
def cq_csggzyjy_ml(html, pre_info):
    links, contents = [], []
    info = copy.deepcopy(pre_info)
    selector = build_etree_xpath(html)
    try:
        if selector.xpath("//span[contains(@id, 'ctl00_ContentPlaceHolder1_myGV_ctl23_LabelPageCount')]/text()"):
            total_page = \
                selector.xpath("//span[contains(@id, 'ctl00_ContentPlaceHolder1_myGV_ctl23_LabelPageCount')]/text()")[0]
        elif selector.xpath("//span[contains(@id, 'ctl00_ContentPlaceHolder1_myGV_ctl15_LabelPageCount')]/text()"):
            total_page = \
                selector.xpath("//span[contains(@id, 'ctl00_ContentPlaceHolder1_myGV_ctl15_LabelPageCount')]/text()")[0]
        total_page = int(total_page)
    except:
        return links, contents

    try:
        current_page = \
            selector.xpath("//span[contains(@id, 'ctl00_ContentPlaceHolder1_myGV_ctl23_LabelCurrentPage')]/text()")[0]
        current_page = int(current_page)
    except:
        current_page = total_page
    print "这是第%s/%s页" % (current_page, total_page)
    if 'csggzyjy' in pre_info[URL]:
        root_url = 'http://www.csggzyjy.com/ceinwz/'
    elif 'cqlpjyzx' in pre_info[URL]:
        root_url = 'http://www.cqlpjyzx.com/ceinwz/'
    elif 'wlzyzx' in pre_info[URL]:
        root_url = 'http://www.wlzyzx.cn/ceinwz/'
    elif 'cqkxjyzx' in pre_info[URL]:
        root_url = 'http://www.cqkxjyzx.com/ceinwz/'

    __VIEWSTATEENCRYPTED = ''
    __EVENTTARGET = 'ctl00$ContentPlaceHolder1$myGV$ctl23$LinkButtonNextPage'
    __EVENTVALIDATION = selector.xpath("//input[contains(@id, '__EVENTVALIDATION')]/@value")[0]
    __VIEWSTATE = selector.xpath("//input[contains(@id, '__VIEWSTATE')]/@value")[0]
    p_data = {
        '__VIEWSTATE': __VIEWSTATE,
        '__EVENTVALIDATION': __EVENTVALIDATION,
        '__EVENTTARGET': __EVENTTARGET,
        'ctl00$ContentPlaceHolder1$DDLPageSize': '20',
        'ctl00_myTreeView_ExpandState': 'nnnnn',
        'linkurl': '_Blank',
        'select5': '_Blank',
        'ctl00_myTreeView_SelectedNode': '',
        '__EVENTARGUMENT': '',
        'ctl00_myTreeView_PopulateLog': '',
        '__LASTFOCUS': '',
        '__VIEWSTATEENCRYPTED': '',
        'ctl00$ContentPlaceHolder1$txtGcmc': '',
        'select': '',
    }
    if 'cqlpjyzx' in pre_info[URL]:
        p_data['linkurl'] = 'http://www.chinabidding.com.cn'
    elif 'wlzyzx' in pre_info[URL] or 'cqkxjyzx' in pre_info[URL]:
        p_data = {
            '__VIEWSTATEENCRYPTED': __VIEWSTATEENCRYPTED,
            '__EVENTVALIDATION': __EVENTVALIDATION,
            '__VIEWSTATE': __VIEWSTATE,
            '__EVENTTARGET': __EVENTTARGET,
        }

    def next_page_func(info, next_page):
        info[METHOD] = POST
        info[PARAMS] = p_data

    links += next_pages(pre_info, next_page_func, current_page, total_page)
    if 'cqkxjyzx' in pre_info[URL] or 'wlzyzx' in pre_info[URL]:
        item_list = selector.xpath("//table[contains(@id, 'ctl00_ContentPlaceHolder1_myGV')]/tr[td[span[contains(@id, 'lblSgzbbm')]]]")
    else:
        item_list = selector.xpath(
            "//table[contains(@id, 'ctl00_ContentPlaceHolder1_myGV')]/tr[td[contains(@class, 'BH')]]")
    for item in item_list:
        info = copy.deepcopy(pre_info)
        info[METHOD] = GET
        ll = info.pop(PARAMS, '')
        if item.xpath("./td/a/font/text()"):
            info[TITLE] = item.xpath("./td/a/font/text()")[0].strip()
        else:
            info[TITLE] = item.xpath("./td/a/text()")[0].strip()
        info[URL] = root_url + item.xpath("./td/a/@href")[0].strip()
        # print info[TITLE]
        if 'csggzyjy' in info[URL]:
            # print etree.tounicode(item)
            if item.xpath("./td/span/font/text()"):
                info[PUBLISHED_TS] = extract_first_date(item.xpath("./td/span/font/text()")[0].strip())
            else:
                info[PUBLISHED_TS] = extract_first_date(
                    item.xpath("./td/span[contains(@style, 'color:Black;')]/text()")[0].strip(), is_str=True)
        elif 'cqkxjyzx' in info[URL] or 'wlzyzx' in info[URL]:
            info[PUBLISHED_TS] = extract_first_date(item.xpath("./td[last()]/text()")[0].strip(), is_str=True)
        links.append(info)
    return links, contents


@add_url(url_filter('http://www.wlzyzx.cn/ceinwz/hyzq/hyzbjggszfcg.aspx'))
@add_url(url_filter('http://www.cqkxjyzx.com/ceinwz/hyzq/hyzbjggszfcg.aspx'))
@add_url(url_filter('http://www.csggzyjy.com/ceinwz/hyzq/hyzbjgggzfcg.aspx'))
@add_url(url_filter('http://www.cqlpjyzx.com/ceinwz/hyzq/hyzbjggszfcg.aspx'))
def cq_csggzyjy_nr(html, pre_info):
    links, contents = [], []
    info = copy.deepcopy(pre_info)
    selector = build_etree_xpath(html)
    if 'csgg' in pre_info[URL]:
        root_url = "http://www.csggzyjy.com"
        content = etree.tounicode(selector.xpath("//iframe[contains(@id, 'frmPdf')]")[0])
    elif 'wlzyzx' in pre_info[URL]:
        root_url = 'http://www.wlzyzx.cn'
        content = etree.tounicode(selector.xpath("//iframe[contains(@id, 'frmPdf')]")[0])
    elif 'cqlp' in pre_info[URL]:
        info[PUBLISHED_TS] = extract_first_date(selector.xpath("//span[contains(@id, 'lblZbgsWzDate')]/text()")[0])
        root_url = "http://www.cqlpjyzx.com"
        content = etree.tounicode(selector.xpath("//iframe[contains(@id, 'frmBestwordHtml')]")[0])
    elif 'cqkxjyzx' in pre_info[URL]:
        root_url = 'http://www.cqkxjyzx.com'
        content = etree.tounicode(selector.xpath("//iframe[contains(@id, 'frmBestwordHtml')]")[0])

    info[CONTENT] = content
    pdf_url = re.findall('src="(\S+)"', content)[0]
    import requests, base64
    real_pdf_uri = root_url + pdf_url
    temp = requests.get(real_pdf_uri).content
    if 'cqlpjyzx' in info[URL]:
        selector = etree.HTML(temp.decode('gbk'))
        content = etree.tounicode(selector.xpath("//table[contains(@class, 'MsoNormalTable')]")[0])
        info[CONTENT] = content
        contents.append(info)
        return links, contents
    elif 'csggzyjy' in pre_info[URL] or 'wlzyzx' in pre_info[URL]:
        if re.findall("src=\"(\S+)\"", temp):
            real_pdf_uri = root_url + '/' + re.findall("src=\"(\S+)\"", temp)[0]
            real_pdf_content = requests.get(real_pdf_uri).content
            pdf_b64 = base64.b64encode(real_pdf_content)
        else:
            print "文件不存在"
            return links, contents
    elif 'cqkxjyzx':
        if 'pdf' in real_pdf_uri:
            print "发现PDF附件,正在进行base64加密"
            pdf_b64 = base64.b64encode(temp)
        else:
            selector = etree.HTML(temp.decode('gbk'))
            content = etree.tounicode(selector.xpath("//div[contains(@class, 'WordSection1')]")[0])
            info[CONTENT] = content
            contents.append(info)
            return links, contents

    info[APPENDIX] = [{
        "scr_url": real_pdf_uri,
        "src_data": pdf_b64,
        'type': 'pdf',
    }]
    contents.append(info)
    return links, contents


@add_url(url_filter("http://www.naggzy.gov.cn/articleWeb!list.action"))
def cq_naggzy_ml(html, pre_info):
    print "parsing :", pre_info[URL]
    print pre_info.get(PARAMS, {})
    # print html
    links, contents = [], []
    selector = etree.HTML(html)
    current_page = (pre_info.get(PARAMS, {}).get("startIndex", 1))
    total_page = re.findall(ur"共(\d+)个记录", html)[0]
    current_page = int(current_page) / 15
    print "正在抓取%s/%s页" % (current_page, int(total_page) / 15)
    total_page = int(total_page) / 15 + 1

    def next_page_func(info, next_page):
        info[URL] = 'http://www.naggzy.gov.cn/articleWeb!list.action'
        info[METHOD] = POST
        info[PARAMS] = {'resourceCode': 'jszbgs', 'startIndex': str(next_page * 15)}

    links += next_pages(pre_info, next_page_func, current_page, total_page)

    root_url = 'http://www.naggzy.gov.cn/'
    item_list = selector.xpath("//table[contains(@class, 'in_ullist')]/tr")
    for item in item_list:
        info = copy.deepcopy(pre_info)
        info[METHOD] = GET
        info[URL] = root_url + item.xpath("./td/a/@href")[0].strip()
        info[TITLE] = item.xpath("./td/a/text()")[0].strip()
        info[PUBLISHED_TS] = extract_first_date(item.xpath("./td/span/text()")[0].strip(), is_str=True)
        links.append(info)

    return links, contents


@add_url(url_filter('http://www.naggzy.gov.cn/articleWeb!view.action?article.id'))
def cq_naggzy_nr(html, pre_info):
    links, contents = [], []
    info = copy.deepcopy(pre_info)
    selector = etree.HTML(html)
    content = etree.tounicode(selector.xpath("//div[contains(@class, 'newsdetail_con')]")[0])
    info[CONTENT] = content
    contents.append(info)
    return links, contents


@add_url(url_filter('http://www.jjqjyzx.com/www/site/site_index_125_'))
def cq_jjqjyzx_ml(html, pre_info):
    links, contents = [], []
    selector = build_etree_xpath(html)
    if not selector.xpath("//td/b/text()"):
        return links, contents
    current_page = int(selector.xpath("//td/b/text()")[0])
    total_page = re.findall(ur'分(\d+)页', html)[0]
    print "正在抓取%s/%s页" % (current_page, total_page)

    def next_page_func(info, next_page):
        info[URL] = 'http://www.jjqjyzx.com/www/site/site_index_125_%s.shtml?' % next_page

    links += next_pages(pre_info, next_page_func, current_page, total_page)
    root_url = 'http://www.jjqjyzx.com/www/site/'
    item_list = selector.xpath("//tr[td[a[img]]]")
    for item in item_list:
        info = copy.deepcopy(pre_info)
        info[TITLE] = item.xpath("./td/a/text()")[0]
        info[URL] = root_url + item.xpath("./td/a/@href")[0]
        info[PUBLISHED_TS] = extract_first_date(item.xpath("./td/font/text()")[0].strip('[]'))
        links.append(info)

    return links, contents


@add_url(url_filter("http://www.jjqjyzx.com/www/site/../site/web_show"))
def cq_jjqjyzx_nr(html, pre_info):
    links, contents = [], []
    info = copy.deepcopy(pre_info)
    selector = build_etree_xpath(html)
    content = etree.tounicode(selector.xpath("//td[@id='textflag']")[0])
    info[CONTENT] = content
    contents.append(info)
    return links, contents


@add_url(url_filter("http://www.yczyjy.cn/WebSite/ProDeal/List"))
def cq_yczyjy_index(html, pre_info):
    links, contents = [], []
    info = copy.deepcopy(pre_info)
    current_page = 1
    post_data = {
        'pageindex': current_page,
        'pagesize': '10',
    }
    info[METHOD] = POST
    info[
        URL] = 'http://www.yczyjy.cn/WebSite/CommonHandler.ashx?form=infoList&action=getList&classID=003001004&classType=2'
    info[PARAMS] = post_data
    links.append(info)
    return links, contents


@add_url(url_filter("http://www.yczyjy.cn/WebSite/CommonHandler.ashx"))
def cq_yczyjy_ml(html, pre_info):
    links, contents = [], []
    res_json = json.loads(html)
    html = res_json.get("showinfo")
    selector = build_etree_xpath(html)
    total_page = res_json.get('pagesum')
    current_page = res_json.get('pageindex')
    print "[%s/%s]" % (current_page, total_page)

    def next_page_func(info, next_page):
        info[PARAMS]['pageindex'] = next_page

    links += next_pages(pre_info, next_page_func, current_page, total_page)
    item_list = selector.xpath("//li")
    for item in item_list:
        info = copy.deepcopy(pre_info)
        info[TITLE] = item.xpath("./a/text()")[0]
        info[URL] = item.xpath("./a/@href")[0]
        info[PUBLISHED_TS] = extract_first_date(item.xpath("./span/text()")[0])
        links.append(info)
    return links, contents


@add_url(url_filter("http://www.yczyjy.cn/WebSite/ProDeal/ZbidView.aspx"))
def cq_yczyjy_nr(html, pre_info):
    links, contents = [], []
    info = copy.deepcopy(pre_info)
    selector = build_etree_xpath(html)
    content = etree.tounicode(selector.xpath("//div[contains(@id, 'dContent')]")[0])
    info[CONTENT] = content
    contents.append(info)
    return links, contents


# ================重  庆================ #
# =================END================= #


# 重庆巫溪县公共资源综合交易中心
@add_url(url_filter("http://www.wuxifz.com/articleWeb!list.action"))
def cq_wxggzy_ml(html, pre_info):
    print "parsing :", pre_info[URL]
    # print pre_info.get(PARAMS, {})
    # print html
    links, contents = [], []
    selector = etree.HTML(html)
    current_page = (pre_info.get(PARAMS, {}).get("startIndex", 1))
    total_page = re.findall(ur"共(\d+)个记录", html)[0]
    current_page = int(current_page) / 15
    total_page = int(math.ceil(float(total_page) / 15))
    print "正在抓取%s/%s页" % (current_page, total_page)

    def next_page_func(info, next_page):
        info[URL] = 'http://www.wuxifz.com/articleWeb!list.action'
        info[METHOD] = POST
        info[PARAMS] = {'resourceCode': 'jszbgs', 'startIndex': str(next_page * 15)}

    links += next_pages(pre_info, next_page_func, current_page, total_page)

    root_url = 'http://www.wuxifz.com/'
    item_list = selector.xpath("//td[contains(@class, 'sub_content')]/ul/li")
    for item in item_list:
        info = copy.deepcopy(pre_info)
        info[METHOD] = GET
        info[URL] = root_url + item.xpath("./a/@href")[0].strip()
        info[TITLE] = item.xpath("./a/text()")[0].strip()
        info[PUBLISHED_TS] = extract_first_date(item.xpath("./span/text()")[0].strip(), is_str=True)
        links.append(info)

    return links, contents


@add_url(url_filter('http://www.wuxifz.com/articleWeb!view.action?article.id='))
def cq_wxggzy_nr(html, pre_info):
    # print json.dumps(pre_info, ensure_ascii=False)
    links, contents = [], []
    info = copy.deepcopy(pre_info)
    selector = etree.HTML(html)
    content = etree.tounicode(selector.xpath("//div[contains(@class, 'newsdetail_con')]")[0])
    info[CONTENT] = content
    contents.append(info)
    return links, contents


# 彭水县公共资源交易网
@add_url(url_filter("http://www.psggzy.com/main/jyjggg/gcjyjjgg/index%s.shtml", "(?:_\d+)?"))
def cq_psxggzy_ml(html, pre_information):
    links, contents = [], []

    # 找到所有列表项目地址
    host = "http://www.psggzy.com"
    bs = build_beautiful_soup(html)
    lst = bs.find("table", attrs={"class": "bottomLineTable"})
    lst = lst.find_all("tr") if lst else []
    for item in lst:
        info = copy.deepcopy(pre_information)
        tds = item.find_all("td")
        t = tds[0].find("a")
        info[URL] = host + t["href"]
        info[TITLE] = t.get_text().strip()
        info[PUBLISHED_TS] = extract_first_date(tds[1].get_text(), is_str=True)
        links.append(info)

    # 找到所有目录后面页地址
    pager = bs.find("td", attrs={"align": "center"})
    next_page = find_tag_with_text(pager, "a", u"下一页")
    if next_page:
        info = copy.deepcopy(pre_information)
        info[URL] = "http://www.psggzy.com/main/jyjggg/gcjyjjgg/" + next_page["href"]
        links.append(info)

    return links, contents


@add_url(url_filter("http://www.psggzy.com/main/jyjggg/%s/Default.shtml", "[\d_]+"))
def cq_psxggzy_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", class_="middle")
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# 云阳县公共资源交易服务中心
@add_url(url_filter("http://www.yyggzyjy.com/Frame/BulletinList.aspx?BusinessType=2&InfoType=2"))
def cq_yyxggzy_ml(html, pre_information):
    links, contents = [], []

    # 找到所有列表项目地址
    html = html.decode('gbk')
    host = "http://www.yyggzyjy.com/Frame/BullitenInfo.aspx?SerialNum="
    selector = etree.HTML(html)
    lst = selector.xpath("//table[contains(@class, 'tblline')]/div/tr")
    for item in lst:
        info = copy.deepcopy(pre_information)
        info[METHOD] = GET
        if PARAMS in info:
            del info[PARAMS]
        t = item.xpath("./td[1]/a/@onclick")[0]
        info[URL] = host + re.findall(u"\d+", t)[0]
        info[TITLE] = item.xpath("./td[1]/a/@title")[0].strip()
        info[PUBLISHED_TS] = extract_first_date(item.xpath("./td[2]/text()")[0], is_str=True)
        links.append(info)

    # 找到所有目录后面页地址
    current_page = pre_information.get(PARAMS, {}).get("__EVENTARGUMENT", 1)
    total_page = selector.xpath("//div[contains(@id, 'Webpager1')]/div[2]/text()")[0]
    total_page = int(re.findall(u"共(\d+)页", total_page)[0])

    print u"当前%s页/%s页" % (current_page, total_page)

    def next_page_func(info, next_page):
        post_data = {
            '__VIEWSTATE': selector.xpath("//input[contains(@id, '__VIEWSTATE')]/@value")[0],
            '__EVENTTARGET': 'Webpager1',
            '__EVENTARGUMENT': next_page,
            '__EVENTVALIDATION': selector.xpath("//input[contains(@id, '__EVENTVALIDATION')]/@value")[0],
            'hButton': 1,
            'Webpager1_input': next_page - 1,
        }
        info[METHOD] = POST
        info[PARAMS] = post_data

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.yyggzyjy.com/Frame/BullitenInfo.aspx?SerialNum="))
def cq_yyxggzy_nr(html, pre_information):
    links, contents = [], []

    # html = html.decode('gbk')
    bs = build_beautiful_soup(html)
    content = bs.find("div", id="divContent")
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================START================ #
# ================天  津================ #

# 天津市政府采购网
@add_url(url_filter("http://www.tjgp.gov.cn/portal/topicView.do"))
def tj_zfcgw_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.tjgp.gov.cn/portal/documentView.do?method=view&"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        info[METHOD] = GET
        t = item.find("a")
        info[URL] = host + t["href"][11:]
        info[TITLE] = t["title"]
        t = item.find("span")
        try:
            info[PUBLISHED_TS] = datetime.datetime.strptime(t.get_text().strip(), "%a %b %d %H:%M:%S %Z %Y").strftime(
                "%Y-%m-%d %H:%M:%S")
        except:
            pass
        links.append(info)

    # 找到所有目录后面页地址
    current_page = pre_information[PARAMS]["page"]
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    pager = bs.find("span", attrs={"class": "countPage"})
    total_page = int(re.findall(u"\d+", pager.get_text())[0])

    def next_page_func(info, next_page):
        info[PARAMS]["page"] = next_page

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.tjgp.gov.cn/portal/documentView.do?method=view&"))
def tj_zfcgw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", attrs={"style": "line-height:25px"})
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# ================天  津================ #
# =================END================= #


# ================START================ #
# ================北  京================ #

# 北京市招投标公共服务平台
@add_url(url_filter("http://www.bjztb.gov.cn/zbjg_2015/index"))
def bj_ztbggfwpt_ml(html, pre_information):
    links, contents = [], []

    host = "http://www.bjztb.gov.cn/zbjg_2015"
    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find_all("table", attrs=dict(border="0", height="25", width="100%", cellpadding="0", cellspacing="0"))
    for item in lst:
        info = copy.deepcopy(pre_information)
        tds = item.find_all("td")[:3]
        t = tds[1].find("a")
        info[URL] = host + t["href"][1:]
        info[TITLE] = t.get_text().strip()
        t = re.findall("\d+\-\d+\-\d+", tds[2].find("script").prettify())[0]
        info[PUBLISHED_TS] = extract_first_date("20" + t, is_str=True)
        links.append(info)

    # 找到所有目录后面页地址
    current_page = re.findall("(?<=index_)\d+", pre_information.get(URL))
    if len(current_page) == 0:
        current_page = 1
    else:
        current_page = int(current_page[0]) + 1
    total_page = 50

    def next_page_func(info, next_page):
        info[URL] = re.sub("index_\d+|index", "index_%s" % (next_page - 1), pre_information[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents


@add_url(url_filter("http://www.bjztb.gov.cn/zbjg_2015/%s/%s.htm", "\d+", "\w+"))
def bj_ztbggfwpt_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("table", attrs=dict(align="center", border="0", width="710", cellpadding="0", cellspacing="0"))
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    summary = bs.find("table", attrs=dict(border="0", width="100%", cellpadding="0", cellspacing="1"))
    if summary:
        trs = summary.find_all("tr")
        summary = {}
        for tr in trs:
            txt = tr.get_text().strip()
            items = txt.split(u"：")
            if len(items) == 2:
                summary[items[0]] = items[1]

        if u"项目单位" in summary:
            info[PURCHASER_NAME] = summary[u"项目单位"]
        if u"招标代理机构" in summary:
            info[AGENT_NAME] = summary[u"招标代理机构"]

    contents.append(info)

    return links, contents


# ================北  京================ #
# =================END================= #


# ================START================ #
# ================全  国================ #

# 中国国际招标网
@add_url(url_filter("http://www.chinabidding.com/search/proj"))
def qg_zggjzbw_ml(html, pre_information):
    links, contents = [], []

    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find("ul", attrs={"class": "as-pager-body"})
    if lst is None:
        return [pre_information], []
    lst = lst.find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        t = item.find("a")
        info[URL] = t["href"]
        info[TITLE] = t.find("span", attrs={"class": "txt"})["title"]
        info[PUBLISHED_TS] = extract_first_date(t.find("span", attrs={"class": "time"}).get_text(), is_str=True)
        attrs = t.find_all("span", attrs={"class": "tag-attr"})
        info[PURCHASE_CATEGORY] = attrs[0].find("strong").get_text()
        info[REGION] = attrs[1].find("strong").get_text()
        info[METHOD] = GET
        links.append(info)

    # 找到所有目录后面页地址
    current_page = int(pre_information.get(PARAMS).get("currentPage"))
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    total_page = 100

    while current_page < total_page:
        next_page_info = copy.deepcopy(pre_information)
        next_page_info[PARAMS]["currentPage"] = str(current_page + 1)
        if pre_information.get(GENERATE_ALL_PAGE):  # 判断是否直接生成后面所有目录页地址
            next_page_info[GENERATED_PAGE] = total_page
            links.append(next_page_info)
            current_page += 1
        else:
            links.append(next_page_info)
            break

    return links, contents


@add_url(url_filter("http://www.chinabidding.com/bidDetail"))
def qg_zggjzbw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", attrs={"class": "as-article-body"})
    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# 中国政府采购招标网
@add_url(url_filter("http://www.chinabidding.org.cn/LuceneSearch.aspx"))
def qg_zgzfcgw_ml(html, pre_information):
    links, contents = [], []

    # 找到所有列表项目地址
    host = "http://www.chinabidding.org.cn/"
    bs = build_beautiful_soup(html)
    lst = bs.find("table", id="TableList").find_all("tr")
    lst = [lst[ind] for ind in range(0, len(lst), 2)]
    for item in lst:
        info = copy.deepcopy(pre_information)
        t = item.find("a")
        info[URL] = host + t["href"]
        links.append(info)

    # 找到所有目录后面页地址
    current_page = int(pre_information.get(PARAMS).get("AspNetPager"))
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    pager = bs.find("span", id="AspNetPager")
    total_page = re.findall(u"总页数:\d+", pager.get_text())[0]
    total_page = re.findall(u"\d+", total_page)[0]
    total_page = int(total_page)

    while current_page < total_page:
        next_page_info = copy.deepcopy(pre_information)
        next_page_info[PARAMS]["AspNetPager"] = str(current_page + 1)
        if pre_information.get(GENERATE_ALL_PAGE):  # 判断是否直接生成后面所有目录页地址
            next_page_info[GENERATED_PAGE] = total_page
            links.append(next_page_info)
            current_page += 1
        else:
            links.append(next_page_info)
            break

    return links, contents


@add_url(url_filter("http://www.chinabidding.org.cn/BidInfoDetails.aspx"))
def qg_zgzfcgw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    title = bs.find("span", id="cphMain_tle").get_text()
    publish_ts = bs.find("span", id="cphMain_tm").get_text()
    content = bs.find("table", id="dinfo")

    info = copy.deepcopy(pre_information)
    info[TITLE] = title
    info[PUBLISHED_TS] = extract_first_date(publish_ts, is_str=True)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    desc = content.find_all("tr")[:3]
    for tr in desc:
        tds = tr.find_all("td")
        if len(tds) == 2:
            key = tds[0].get_text().strip()
            value = tds[1].get_text().strip()
            if key == u"项目编号:" and len(value) > 0:
                info[PROJECT_ID] = value
            elif key == u"所在地区:" and len(value) > 0:
                info[REGION] = value
            elif key == u"所属行业:" and len(value) > 0:
                info[PURCHASE_CATEGORY] = value

    contents.append(info)

    return links, contents


# TODO
# 中国电子招标信息网
@add_url(url_filter("http://www.zbs365.com/zhongbiao/type"))
def qg_zgdzzbw_ml(html, pre_information):
    links, contents = [], []

    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find_all("table")[1]
    lst = lst.find_all("tr")
    lst = lst[1:]
    for item in lst:
        info = copy.deepcopy(pre_information)
        tds = item.find_all("td")
        info[REGION] = tds[0].get_text().strip()
        info[URL] = tds[1].find("a")["href"]
        info[TITLE] = tds[1].get_text().strip()
        info[PURCHASE_CATEGORY] = tds[2].get_text().strip()
        info[PUBLISHED_TS] = extract_first_date(tds[3].get_text(), is_str=True)
        links.append(info)

    # 找到所有目录后面页地址
    current_page = re.findall("\d+", pre_information.get(URL))[1]
    current_page = int(current_page)
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    total_page = 300

    while current_page < total_page:
        next_page_info = copy.deepcopy(pre_information)
        next_page_info[URL] = "http://www.zbs365.com/zhongbiao/type-p{0}.html".format(current_page + 1)
        if pre_information.get(GENERATE_ALL_PAGE):  # 判断是否直接生成后面所有目录页地址
            next_page_info[GENERATED_PAGE] = total_page
            links.append(next_page_info)
            current_page += 1
        else:
            links.append(next_page_info)
            break

    return links, contents


@add_url(url_filter("http://www.zbs365.com/zb/info"))
def qg_zgdzzbw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", id="content")

    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    contents.append(info)

    return links, contents


# 中国政府采购网
@add_url(url_filter("http://www.ccgp.gov.cn/cggg/%s/%s/%s.htm", "\w+", "\w+", "\w+"))
def qg_zgzfcgw_ml(html, pre_information):
    links, contents = [], []

    # 找到所有列表项目地址
    bs = build_beautiful_soup(html)
    lst = bs.find("div", attrs={"class": "main_list"}).find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        t = item.find("a")
        host = re.findall(u"http\://[a-z\.]*/[a-z]*/[a-z]*/[a-z]*/", pre_information[URL])[0]
        info[URL] = host + t["href"][2:]
        info[TITLE] = html_unescape(t["title"])
        t = item.find_all("span")
        info[PUBLISHED_TS] = extract_first_date(t[0].get_text(), is_str=True)
        info[REGION] = t[1].get_text().strip()
        info[PURCHASER_NAME] = t[2].get_text().strip()
        links.append(info)

    # 找到所有目录后面页地址
    current_page = re.findall("(?<=index_)\d+", pre_information.get(URL))
    if len(current_page) == 0:
        current_page = 1
    else:
        current_page = int(current_page[0]) + 1
    if pre_information.get(GENERATED_PAGE):
        current_page = max(current_page, pre_information.get(GENERATED_PAGE))
    total_page = 25

    while current_page < total_page:
        next_page_info = copy.deepcopy(pre_information)
        next_page_info[URL] = re.sub("index(?:_\d+|)", "index_%s" % current_page, next_page_info[URL])
        if pre_information.get(GENERATE_ALL_PAGE):  # 判断是否直接生成后面所有目录页地址
            next_page_info[GENERATED_PAGE] = total_page
            links.append(next_page_info)
            current_page += 1
        else:
            links.append(next_page_info)
            break

    return links, contents


@add_url(url_filter("http://www.ccgp.gov.cn/cggg/%s/%s/%s/%s.htm", "\w+", "\w+", "\w+", "\w+"))
@add_url(url_filter("http://search.ccgp.gov.cn/bidDetailShow.jsp?bidDoc="))
def qg_zgzfcgw_nr(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    content = bs.find("div", attrs={"class": "vT_detail_content w760c"})

    info = copy.deepcopy(pre_information)
    if PRE_PURIFY_CONTENT:
        content = html_purify(content)
    info[CONTENT] = str(content)

    summary = bs.find("div", attrs={"class": "table"})
    if summary:
        summary = summary.find("table")
    if summary:
        tds = summary.find_all("td")
        tds = tds[1:19] + tds[20:36]
        summary = {}
        for i in range(0, len(tds) - 1, 2):
            summary[tds[i].get_text().strip()] = tds[i + 1].get_text().strip()

        if u"采购项目名称" in summary and summary[u"采购项目名称"] != u"详见公告正文":
            info[PROJECT_NAME] = summary[u"采购项目名称"]
        if u"品目" in summary and summary[u"品目"] != u"详见公告正文":
            info[PURCHASE_CATEGORY] = summary[u"品目"]
        if u"本项目招标公告日期" in summary and summary[u"本项目招标公告日期"] != u"详见公告正文":
            info[ANNOUNCED_TS] = extract_first_date(summary[u"本项目招标公告日期"], is_str=True)
        if u"项目联系人" in summary and summary[u"项目联系人"] != u"详见公告正文":
            info[PROJECT_CONTACT_NAME] = summary[u"项目联系人"]
        if u"项目联系电话" in summary and summary[u"项目联系电话"] != u"详见公告正文":
            info[PROJECT_CONTACT_PHONE] = summary[u"项目联系电话"]
        if u"成交日期" in summary and summary[u"成交日期"] != u"详见公告正文":
            info[DEAL_TS] = extract_first_date(summary[u"成交日期"], is_str=True)
        if u"中标日期" in summary and summary[u"中标日期"] != u"详见公告正文":
            info[WINNING_TS] = extract_first_date(summary[u"中标日期"], is_str=True)
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

    contents.append(info)

    return links, contents


# 中国政府采购网-搜索结果

@add_url(url_filter("http://search.ccgp.gov.cn/bxsearch$"))
def gen_search_msg(html, pre_information):
    links, contents = [], []

    url_temp = "http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=1&bidSort=0&buyerName=&projectId=&pinMu=0&bidType={bt}&dbselect=bidx&kw=&start_time={st}&end_time={et}&timeType=3&displayZone=&zoneId=&pppStatus=0&agentName="

    now = datetime.datetime.now()
    delta = datetime.timedelta(days=14)
    end_ts = now.strftime("%Y:%m:%d")
    start_ts = (now - delta).strftime("%Y:%m:%d")

    # 中标公告
    info = copy.deepcopy(pre_information)
    info[ANNOUNCE_TYPE] = u"中标公告"
    info[URL] = url_temp.format(bt=7, st=start_ts, et=end_ts)
    links.append(info)

    # 成交公告
    info = copy.deepcopy(pre_information)
    info[ANNOUNCE_TYPE] = u"成交公告"
    info[URL] = url_temp.format(bt=11, st=start_ts, et=end_ts)
    links.append(info)

    return links, contents


@add_url(url_filter("http://search.ccgp.gov.cn/bxsearch?searchtype=1"))
def qg_ccgp_list_page(html, pre_information):
    links, contents = [], []

    bs = build_beautiful_soup(html)
    lst = bs.find("ul", attrs={"class": "vT-srch-result-list-bid"}).find_all("li")
    for item in lst:
        info = copy.deepcopy(pre_information)
        info[SLEEP_SECOND] = 0
        a = item.find("a")
        info[URL] = a["href"]
        info[TITLE] = a.get_text().strip()
        span = item.find("span")
        txt = span.get_text().strip()
        its = [_.strip() for _ in txt.split("|")]
        info[PUBLISHED_TS] = extract_first_date(its[0])
        if its[1].startswith(u"采购人："):
            info[PURCHASER_NAME] = its[1][4:]
        if its[2].startswith(u"代理机构："):
            info[AGENT_NAME] = its[2][5:].split("\r\n")[0].strip()
        if its[4]:
            info[PURCHASE_CATEGORY] = its[4]
        links.append(info)

    pager = bs.find("p", attrs={"class": "pager"})
    page_ids = re.findall("\d+", pager.get_text())
    page_ids = [int(idx) for idx in page_ids]
    total_page = max(page_ids)
    current_page = int(re.findall("(?<=page_index=)\d+", pre_information[URL])[0])

    def next_page_func(info, next_page):
        info[URL] = re.sub("page_index=\d+", "page_index=%s" % next_page, info[URL])

    links += next_pages(pre_information, next_page_func, current_page, total_page)

    return links, contents

# ================全  国================ #
# =================END================= #
