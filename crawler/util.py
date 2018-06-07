# coding=utf-8
# author="Jianghua Zhao"

import bs4
import re
import datetime
import time
from urllib import urlencode, unquote
from lxml import etree
import HTMLParser

_html_parser = HTMLParser.HTMLParser()


def html_unescape(html):
    return _html_parser.unescape(html)


def build_beautiful_soup(html):
    bs = bs4.BeautifulSoup(html, "html.parser")
    return bs


def build_etree_xpath(html):
    selector = etree.HTML(html)
    return selector


def url_encode(url):
    encode_url = urlencode({"url": url})[4:]
    return encode_url


def url_decode(url):
    return unquote(url)


def find_tag_with_text(tag, name, text):
    # def func(x):
    #     return isinstance(x, bs4.Tag) and x.name == name and text in x.get_text()

    return tag.find(lambda x: isinstance(x, bs4.Tag) and x.name == name and text in x.get_text())


def on_schedule(schedule_seconds):
    now = datetime.datetime.now()
    current_second = now.hour * 3600 + now.minute * 60 + now.second
    schedule_seconds = sorted(schedule_seconds)
    for scd in schedule_seconds:
        if scd > current_second:
            sleep_second = scd - current_second
            time.sleep(sleep_second)
            break


def get_host_address(url):
    url = url.replace("http://", "")
    url = url.replace("https://", "")
    url = url.replace("?", "/")
    return url.split("/")[0]


"""
定义中标公告统一的属性
"""
# 公告信息
ORIGIN_REGION = "origin_region"  # 起始区域,网站所属区域，包括全国及各个省和直辖市
URL = "url"  # 公告网页地址， 用于用户访问网页查看原公告使用
DATA_URL = "data_url"  # 公告数据地址，用于爬虫爬取数据使用
TITLE = "title"
CONTENT = "content"  # 公告网页内容
APPENDIX = 'appendix'

ANNOUNCE_TYPE = "announce_type"  # 公告类型（中标公告、成交公告、、、）
REGION = "region"  # 公告项目所属行政区域
WEBSITE = "website"  # 网站名称
NOTE = "note"  # 备注

# 公告时间信息
PUBLISHED_TS = "published_ts"  # 公告时间--网页发布时间
ANNOUNCED_TS = "announced_ts"  # 本项目招标公告日期
WINNING_TS = "winning_ts"  # 中标日期
DEAL_TS = "deal_ts"  # 成交日期
OPEN_BID_TS = "open_bid_ts"  # 开标日期
EVALUATE_TS = "evaluate_ts"  # 评标/评审时间
END_BID_TS = "end_bid_ts"  # 结标时间

# 项目信息
PROJECT_NAME = "project_name"
PROJECT_ID = "project_id"
PROJECT_CONTACT_NAME = "project_contact_name"
PROJECT_CONTACT_PHONE = "project_contact_phone"
PROJECT_TYPE = "project_type"  # 项目类型（政府采购、工程建设、矿产交易、产权交易、土地交易、、）
PROJECT_BUDGET = "project_budget"  # 项目预算

PURCHASE_CATEGORY = "purchase_category"  # 采购品目
PURCHASE_TYPE = "purchase_type"  # 采购类型（公开招标、竞争性谈判、单一来源采购、询价采购、、）

# 采购单位信息
PURCHASER_NAME = "purchaser_name"
PURCHASER_ADDRESS = "purchaser_address"
PURCHASER_CONTACT_NAME = "purchaser_contact_name"
PURCHASER_CONTACT_PHONE = "purchaser_contact_phone"

# 采购代理机构信息
AGENT_NAME = "agent_name"
AGENT_ADDRESS = "agent_address"
AGENT_CONTACT_NAME = "agent_contact_name"
AGENT_CONTACT_PHONE = "agent_contact_phone"

# 中标信息
BIDDING_RESULT = "bidding_result"

EXPERT_NAMES = "expert_names"  # 评审专家名单

TOTAl_WINNING_MONEY = "total_winning_money"  # 总中标金额

SEGMENTS = "segments"  # 公告标段列表
SEGMENT_NAME = "segment_name"  # 标段名

WINNER = "winner"  # 标段中标人
WINNING_COMPANY_NAME = "winning_company_name"  # 中标单位名称
WINNING_COMPANY_ADDRESS = "winning_company_address"  # 中标单位地址
WINNING_MONEY = "winning_money"  # 中标金额

CANDIDATES = "candidates"  # 标段候选人
CANDIDATE_COMPANY_NAME = "candidate_company_name"  # 候选单位名称
CANDIDATE_COMPANY_ADDRESS = "candidate_company_address"  # 候选单位地址
CANDIDATE_MONEY = "candidate_money"  # 候选中标金额
CANDIDATE_RANK = "candidate_rank"  # 候选排序

# MONEY 属性
MONEY_AMOUNT = "money_amount"  # 金额
MONEY_UNIT = "money_unit"  # 单位
MONEY_CURRENCY = "money_currency"  # 币种

# 其他信息
OTHERS = "others"

# 公告属性列表
ANNOUNCE_PROPERTY_LIST = [URL, DATA_URL, TITLE, CONTENT, ANNOUNCE_TYPE, PUBLISHED_TS, ANNOUNCED_TS, WINNING_TS, DEAL_TS,
                          OPEN_BID_TS, EVALUATE_TS, END_BID_TS, ORIGIN_REGION, REGION, WEBSITE, NOTE, APPENDIX,

                          PROJECT_NAME, PROJECT_ID, PROJECT_CONTACT_NAME, PROJECT_CONTACT_PHONE, PROJECT_TYPE,
                          PURCHASE_CATEGORY, PURCHASE_TYPE,

                          PURCHASER_NAME, PURCHASER_ADDRESS, PURCHASER_CONTACT_NAME, PURCHASER_CONTACT_PHONE,

                          AGENT_NAME, AGENT_ADDRESS, AGENT_CONTACT_NAME, AGENT_CONTACT_PHONE,

                          BIDDING_RESULT, EXPERT_NAMES, TOTAl_WINNING_MONEY, SEGMENT_NAME, WINNING_COMPANY_NAME,
                          WINNING_COMPANY_ADDRESS, WINNING_MONEY, CANDIDATE_COMPANY_NAME, CANDIDATE_COMPANY_ADDRESS,
                          CANDIDATE_MONEY, CANDIDATE_RANK,

                          OTHERS]

"""
定义爬虫爬取时的状态变量
"""
UNI_ORIGIN_ID = "uni_origin_id"  # 数据源唯一标示

TOTAl_PAGE = "total_page"  # 总页码(int)
CURRENT_PAGE = "current_page"  # 当前页码，从1开始计数(int)
GENERATE_ALL_PAGE = "generate_all_page"  # 是否生成所有目录页(True, False)
GENERATED_PAGE = "generated_page"  # 已经生成的最大页码(int)
SLEEP_SECOND = "sleep_second"  # 爬取网页间隔时间

CRAWLED_COUNT = "crawled_count"  # 网页被爬取次数(int)
BEYOND_TIME_COUNT = "beyond_time_count"  # 超过起始时间的次数
METHOD = "method"  # 网页请求方式
PARAMS = "params"  # 请求参数

"""
定义爬虫爬取某个url时的临时变量
"""
NO_CONTENT_TIMES = "no_content_times"  # 没有内容次数
SLEEP_FOR_CONTENT = "sleep_for_content"  # 在获取内容前sleep的时间

"""
爬虫配置
"""
MAX_CRAWLER_NUMBER = "max_crawler_number"  # 最多一次可以启动的爬虫数量

# 临时变量列表
STATUS_VARIABLE_LIST = [UNI_ORIGIN_ID, TOTAl_PAGE, CURRENT_PAGE, GENERATE_ALL_PAGE, GENERATED_PAGE, SLEEP_SECOND,
                        CRAWLED_COUNT, BEYOND_TIME_COUNT, METHOD, PARAMS,
                        MAX_CRAWLER_NUMBER]
# 针对单个url的变量
TMP_VARIABLE_LIST = [NO_CONTENT_TIMES, SLEEP_FOR_CONTENT]

"""
网页请求方式
"""
GET = "GET"
POST = "POST"

"""
招投标地区编码
"""
BID_REGION_CODE_TABLE = {u"台湾": "tai_wan", u"澳门": "ao_men", u"香港": "xiang_gang", u"宁夏": "ning_xia", u"广西": "guang_xi",
                         u"西藏": "xi_zhang", u"新疆": "xing_jiang", u"内蒙古": "nei_meng_gu", u"海南": "hai_nan",
                         u"广东": "guang_dong", u"云南": "yun_nan", u"贵州": "gui_zhou", u"青海": "qing_hai", u"甘肃": "gan_su",
                         u"四川": "si_chuan", u"江西": "jiang_xi", u"福建": "fu_jian", u"安徽": "an_hui", u"浙江": "zhe_jiang",
                         u"江苏": "jiang_su", u"吉林": "ji_lin", u"辽宁": "liao_ning", u"黑龙江": "hei_long_jiang",
                         u"湖南": "hu_nan", u"湖北": "hu_bei", u"陕西": "shan_xi-", u"山东": "shan_dong", u"山西": "shan_xi_",
                         u"河南": "he_nan", u"河北": "he_bei", u"上海": "shang_hai", u"重庆": "chong_qing", u"天津": "tian_jin",
                         u"北京": "bei_jing", u"全国": "quan_guo",}
