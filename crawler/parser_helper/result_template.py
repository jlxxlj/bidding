# coding=utf-8
# author="Jianghua Zhao"


from keywords import *


def result_template():
    result = {
        URL: None,  # 公告网页地址， 用于用户访问网页查看原公告使用
        DATA_URL: None,  # 公告数据地址，用于爬虫爬取数据使用
        TITLE: None,
        # CONTENT: None,  # 公告网页内容
        ANNOUNCE_TYPE: None,  # 公告类型（中标公告、成交公告、、、）
        PUBLISHED_TS: None,  # 公告时间--网页发布时间
        ANNOUNCED_TS: None,  # 本项目招标公告日期
        WINNING_TS: None,  # 中标日期
        DEAL_TS: None,  # 成交日期
        OPEN_BID_TS: None,  # 开标日期
        EVALUATE_TS: None,  # 评标时间
        END_BID_TS: None,  # 结标时间

        ORIGIN_REGION: None,  # 起始区域,网站所属区域，包括全国及各个省和直辖市
        REGION: None,  # 行政区域
        WEBSITE: None,  # 网站名称
        NOTE: None,  # 备注

        # 项目信息
        PROJECT_NAME: None,
        PROJECT_ID: None,
        PROJECT_CONTACT_NAME: None,
        PROJECT_CONTACT_PHONE: None,
        PROJECT_TYPE: None,  # 项目类型（政府采购、工程建设、矿产交易、产权交易、土地交易、、）
        PROJECT_BUDGET: None,  # 项目预算

        PURCHASE_CATEGORY: None,  # 采购品目
        PURCHASE_TYPE: None,  # 采购类型（公开招标、竞争性谈判、单一来源采购、询价采购、、）

        # 采购单位信息
        PURCHASER_NAME: None,
        PURCHASER_ADDRESS: None,
        PURCHASER_CONTACT_NAME: None,
        PURCHASER_CONTACT_PHONE: None,

        # 采购代理机构信息
        AGENT_NAME: None,
        AGENT_ADDRESS: None,
        AGENT_CONTACT_NAME: None,
        AGENT_CONTACT_PHONE: None,

        # 中标信息
        EXPERT_NAMES: None,  # 评审专家名单
        TOTAl_WINNING_MONEY: None,  # 总中标金额
        SEGMENTS: []
    }
    return result


def segment_template():
    segment = {
        SEGMENT_NAME: None,
        WINNER: None,
        CANDIDATES: []
    }
    return segment


def winner_template():
    winner = {
        WINNING_COMPANY_NAME: None,  # 中标单位名称
        WINNING_COMPANY_ADDRESS: None,  # 中标单位地址
        WINNING_MONEY: None,  # 中标金额
    }
    return winner


def candidate_template():
    candidate = {
        CANDIDATE_COMPANY_NAME: None,  # 候选单位名称
        CANDIDATE_COMPANY_ADDRESS: None,  # 候选单位地址
        CANDIDATE_MONEY: None,  # 候选中标金额
        CANDIDATE_RANK: None  # 候选排序
    }
    return candidate


def money_template():
    money = {
        MONEY_AMOUNT: None,  # 金额
        MONEY_UNIT: None,  # 单位
        MONEY_CURRENCY: None  # 币种
    }
    return money
