# coding=utf-8
# author="Jianghua Zhao"

import bs4
import datetime
import time
from urllib import urlencode, unquote

"""
定义中标公告统一的属性
"""
# 公告信息
ORIGIN_REGION = "origin_region"  # 起始区域,网站所属区域，包括全国及各个省和直辖市
URL = "url"  # 公告网页地址， 用于用户访问网页查看原公告使用
DATA_URL = "data_url"  # 公告数据地址，用于爬虫爬取数据使用
TITLE = "title"
CONTENT = "content"  # 公告网页内容

ANNOUNCE_TYPE = "announce_type"  # 公告类型（中标公告、成交公告、、、）
REGION = "region"  # 公告项目所属行政区域
WEBSITE = "website"  # 网站名称
NOTE = "note"  # 备注

# 公告时间信息
PUBLISHED_TS = "published_ts"  # 公告时间--网页发布时间
ANNOUNCED_TS = "announced_ts"  # 本项目招标公告日期
OPEN_BID_TS = "open_bid_ts"  # 开标日期
EVALUATE_TS = "evaluate_ts"  # 评标/评审时间
WINNING_TS = "winning_ts"  # 中标日期
DEAL_TS = "deal_ts"  # 成交日期
END_BID_TS = "end_bid_ts"  # 结标时间

# 项目信息
PROJECT_NAME = "project_name"
PROJECT_ID = "project_id"
PROJECT_CONTACT_NAME = "project_contact_name"
PROJECT_CONTACT_PHONE = "project_contact_phone"
PROJECT_TYPE = "project_type"  # 项目类型（政府采购、工程建设、矿产交易、产权交易、土地交易、、）
#                                [工程建设项目招投标、土地使用权和矿业权出让、国有产权交易、政府采购]
PROJECT_BUDGET = "project_budget"  # 项目预算

PURCHASE_CATEGORY = "purchase_category"  # 采购品目 (货物类、 工程类、 服务类)
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

ROLE_NAME = "role_name"  # 组织实体在项目中扮演的角色

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
                          OPEN_BID_TS, EVALUATE_TS, END_BID_TS, ORIGIN_REGION, REGION, WEBSITE, NOTE,

                          PROJECT_NAME, PROJECT_ID, PROJECT_CONTACT_NAME, PROJECT_CONTACT_PHONE, PROJECT_TYPE,
                          PURCHASE_CATEGORY, PURCHASE_TYPE,

                          PURCHASER_NAME, PURCHASER_ADDRESS, PURCHASER_CONTACT_NAME, PURCHASER_CONTACT_PHONE,

                          AGENT_NAME, AGENT_ADDRESS, AGENT_CONTACT_NAME, AGENT_CONTACT_PHONE,

                          ROLE_NAME,

                          BIDDING_RESULT, EXPERT_NAMES, TOTAl_WINNING_MONEY, SEGMENT_NAME, WINNING_COMPANY_NAME,
                          WINNING_COMPANY_ADDRESS, WINNING_MONEY, CANDIDATE_COMPANY_NAME, CANDIDATE_COMPANY_ADDRESS,
                          CANDIDATE_MONEY, CANDIDATE_RANK,

                          OTHERS]

# 定义元数据类型元素
ELEM_TYPE_COMPANY_NAME = "company_name"
ELEM_TYPE_DATETIME = "datetime"
ELEM_TYPE_MONEY = "money"
ELEM_TYPE_MONEY_AMOUNT = "money_amount"
ELEM_TYPE_MONEY_UNIT = "money_unit"
ELEM_TYPE_MONEY_CURRENCY = "money_currency"
ELEM_TYPE_PERSON_NAME = "person_name"
ELEM_TYPE_PHONE_NUMBER = "phone_number"
ELEM_TYPE_ADDRESS = "address"
ELEM_TYPE_USUAL_TEXT = "usual_text"
ELEM_TYPE_NUMBER = "number"
ELEM_TYPE_CANDIDATE_RANK = "candidate_rank"
ELEM_TYPE_ROLE_NAME = "role_name"
ELEM_TYPE_PROJECT_ID = "project_id"

# 加权方式
ADD_WEIGHT = 0  # 加
MUT_WEIGHT = 1  # 乘

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
