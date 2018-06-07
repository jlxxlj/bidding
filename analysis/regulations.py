# coding=utf-8
# author="Jianghua Zhao"

import re
import sys

from announce_attributes import *

reload(sys)
sys.setdefaultencoding('utf-8')

POS_PRE = 0
POS_INN = 1
POS_SUF = 2


class Regulation(object):
    def __init__(self, position, re_string, inter_cha=None, inter_len=None):
        print re_string
        self.position = position
        if inter_cha and inter_len and POS_PRE == position:
            re_string = u"(?:%s)[%s]{,%s}$" % (re_string, inter_cha, inter_len)
        elif inter_cha and inter_len and POS_SUF == position:
            re_string = u"^[%s]{,%s}(?:%s)" % (inter_cha, inter_len, re_string)
        self.re_pattern = re.compile(re_string)

    def evaluate(self, pre, inn, suf):
        if POS_PRE == self.position:
            obj = unicode(str(pre))
        elif POS_INN == self.position:
            obj = unicode(str(inn))
        elif POS_SUF == self.position:
            obj = unicode(str(suf))
        if self.re_pattern.search(obj):
            return True
        else:
            return False


SPS = u"^，；。？！,;?!\n"
Reg = Regulation

FIELD_REGS = [
    {"field_name": ANNOUNCED_TS,
     "elem_type": ELEM_TYPE_DATETIME,
     "regulations": [
         [Reg(POS_PRE, u"(?:采购|招标)公告(?:发布|)(?:日期|时间)", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_SUF, u"公开招标", SPS, 5), 1, ADD_WEIGHT]]},

    {"field_name": WINNING_TS,
     "elem_type": ELEM_TYPE_DATETIME,
     "regulations": [
         [Reg(POS_PRE, u"(?:中标|定标)(?:日期|时间)", SPS, 10), 1, ADD_WEIGHT]]},

    {"field_name": DEAL_TS,
     "elem_type": ELEM_TYPE_DATETIME,
     "regulations": [
         [Reg(POS_PRE, u"成交(?:日期|时间)", SPS, 10), 1, ADD_WEIGHT]]},

    {"field_name": OPEN_BID_TS,
     "elem_type": ELEM_TYPE_DATETIME,
     "regulations": [
         [Reg(POS_PRE, u"开标(?:日期|时间)", SPS, 10), 1, ADD_WEIGHT]]},

    {"field_name": EVALUATE_TS,
     "elem_type": ELEM_TYPE_DATETIME,
     "regulations": [
         [Reg(POS_PRE, u"(?:评标|评审)(?:日期|时间)", SPS, 10), 1, ADD_WEIGHT]]},

    {"field_name": END_BID_TS,
     "elem_type": ELEM_TYPE_DATETIME,
     "regulations": [
         [Reg(POS_PRE, u"结标(?:日期|时间)", SPS, 10), 1, ADD_WEIGHT]]},

    {"field_name": PROJECT_NAME,
     "elem_type": ELEM_TYPE_USUAL_TEXT,
     "regulations": [
         [Reg(POS_PRE, u"(?:项目|工程)名称", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:项目|工程)信息", SPS, 15), 2, MUT_WEIGHT]]},

    {"field_name": PROJECT_ID,
     "elem_type": ELEM_TYPE_PROJECT_ID,
     "regulations": [
         [Reg(POS_PRE, u"(?:项目|工程)编?号", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:项目|工程)信息", SPS, 15), 2, MUT_WEIGHT]]},

    {"field_name": PROJECT_CONTACT_NAME,
     "elem_type": ELEM_TYPE_PERSON_NAME,
     "regulations": [
         [Reg(POS_PRE, u"联系人|联系方式", SPS, 10), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:项目|工程)(?:联系人|联系方式)", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:项目|工程)信息", SPS, 15), 2, MUT_WEIGHT]]},

    {"field_name": PROJECT_CONTACT_PHONE,
     "elem_type": ELEM_TYPE_PHONE_NUMBER,
     "regulations": [
         [Reg(POS_PRE, u"电话|联系电话|联系方式", SPS, 10), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:项目|工程)(?:电话|联系电话|联系方式)", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:项目|工程)信息", SPS, 15), 2, MUT_WEIGHT]]},

    # {"field_name": PROJECT_TYPE,
    #  "elem_type": ELEM_TYPE_USUAL_TEXT,
    #  "regulations": [
    #      [Reg(POS_PRE, u"项目类型", SPS, 10), 1, ADD_WEIGHT],
    #      [Reg(POS_PRE, u"项目信息", SPS, 15), 2, MUT_WEIGHT]]},

    {"field_name": PROJECT_BUDGET,
     "elem_type": ELEM_TYPE_MONEY,
     "regulations": [
         [Reg(POS_PRE, u"总?预算(?:金额|)", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:项目|工程)总?预算", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"招标控制价", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:项目|工程)(?:信息|(?:简要)?说明)", SPS, 15), 2, MUT_WEIGHT]]},

    {"field_name": PURCHASE_CATEGORY,
     "elem_type": ELEM_TYPE_USUAL_TEXT,
     "regulations": [
         [Reg(POS_PRE, u"采购品目|货物类型", SPS, 10), 1, ADD_WEIGHT]]},

    {"field_name": PURCHASE_TYPE,
     "elem_type": ELEM_TYPE_USUAL_TEXT,
     "regulations": [
         [Reg(POS_PRE, u"采购类型|采购方式", SPS, 10), 1, ADD_WEIGHT]]},

    {"field_name": PURCHASER_NAME,
     "elem_type": ELEM_TYPE_COMPANY_NAME,
     "regulations": [
         [Reg(POS_PRE, u"(?:采购|招标)(?:人|单位|机构)(?:名称|)", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:采购|招标)(?:人|单位|机构)信息", SPS, 15), 2, MUT_WEIGHT]]},

    {"field_name": PURCHASER_ADDRESS,
     "elem_type": ELEM_TYPE_ADDRESS,
     "regulations": [
         [Reg(POS_PRE, u"地址", SPS, 10), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:采购|招标)(?:人|单位|机构)地址", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:采购|招标)(?:人|单位|机构)信息", SPS, 15), 2, MUT_WEIGHT]]},

    {"field_name": PURCHASER_CONTACT_NAME,
     "elem_type": ELEM_TYPE_PERSON_NAME,
     "regulations": [
         [Reg(POS_PRE, u"联系人|联系方式", SPS, 10), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:采购|招标)(?:人|单位|机构|)(?:联系人|联系方式)", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:采购|招标)(?:人|单位|机构)信息", SPS, 15), 2, MUT_WEIGHT]]},

    {"field_name": PURCHASER_CONTACT_PHONE,
     "elem_type": ELEM_TYPE_PHONE_NUMBER,
     "regulations": [
         [Reg(POS_PRE, u"电话|联系电话|联系方式", SPS, 10), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:采购|招标)(?:人|单位|机构|)(?:电话|联系电话|联系方式)", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:采购|招标)(?:人|单位|机构)信息", SPS, 15), 2, MUT_WEIGHT]]},

    {"field_name": AGENT_NAME,
     "elem_type": ELEM_TYPE_COMPANY_NAME,
     "regulations": [
         [Reg(POS_PRE, u"(?:采购|招标|)代理(?:人|单位|机构)(?:名称|)", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"填报单位", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:采购|招标|)代理(?:人|单位|机构)信息", SPS, 15), 2, MUT_WEIGHT]]},

    {"field_name": AGENT_ADDRESS,
     "elem_type": ELEM_TYPE_ADDRESS,
     "regulations": [
         [Reg(POS_PRE, u"地址", SPS, 10), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:采购|招标|)代理(?:人|单位|机构)地址", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:采购|招标|)代理(?:人|单位|机构)信息", SPS, 15), 2, MUT_WEIGHT]]},

    {"field_name": AGENT_CONTACT_NAME,
     "elem_type": ELEM_TYPE_PERSON_NAME,
     "regulations": [
         [Reg(POS_PRE, u"联系人|联系方式", SPS, 10), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:采购|招标|)代理(?:人|单位|机构)(?:联系人|联系方式)", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"填报人", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:采购|招标|)代理(?:人|单位|机构)信息", SPS, 15), 2, MUT_WEIGHT]]},

    {"field_name": AGENT_CONTACT_PHONE,
     "elem_type": ELEM_TYPE_PHONE_NUMBER,
     "regulations": [
         [Reg(POS_PRE, u"电话|联系电话|联系方式", SPS, 10), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:采购|招标|)代理(?:人|单位|机构)(?:电话|联系电话|联系方式)", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:采购|招标|)代理(?:人|单位|机构)信息", SPS, 15), 2, MUT_WEIGHT]]},

    {"field_name": EXPERT_NAMES,
     "elem_type": ELEM_TYPE_USUAL_TEXT,
     "regulations": [
         [Reg(POS_PRE, u"(?:谈判|评审|评标)(?:小组|委员会)(?:专家)?(?:成员)?(?:名单)?", SPS, 30), 1, ADD_WEIGHT]]},

    {"field_name": TOTAl_WINNING_MONEY,
     "elem_type": ELEM_TYPE_MONEY,
     "regulations": [
         [Reg(POS_PRE, u"总(?:中标|成交)(?:（成交）|（中标）|（选）|)?金?额", SPS, 10), 1, ADD_WEIGHT]]},

    {"field_name": ROLE_NAME,
     "elem_type": ELEM_TYPE_ROLE_NAME,
     "regulations": [
         [Reg(POS_PRE, u"", SPS, 0), 1, ADD_WEIGHT]]},

    {"field_name": WINNING_COMPANY_NAME,
     "elem_type": ELEM_TYPE_COMPANY_NAME,
     "regulations": [
         [Reg(POS_PRE, u"(?:报价单位|报价人|供应商|供货商|服务商|投标人|投标单位)", SPS, 10), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"第一", SPS, 5), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:中标|成交)(?:（成交）|（中标）|（选）|)?(?:推荐)?(?:单位|供应商|供货商|服务商|商|人)", SPS, 30), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:报价单位|报价人|供应商|供货商|服务商|投标人|投标单位)名称", SPS, 10), 0.3, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:中标|成交)(?:（成交）|（中标）|（选）|)?(?:推荐)?(?:单位|供应商|供货商|服务商|商|人)名称", SPS, 30), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:单位|供应商|供货商|服务商|商|人)名称", SPS, 10), 0.1, ADD_WEIGHT],
         [Reg(POS_SUF, u"(?:报价单位|报价人|供应商|供货商|服务商|投标人|投标单位)(?:名称|)", SPS, 10), 0.5, ADD_WEIGHT],
         [Reg(POS_SUF, u"(?:中标|成交)(?:（成交）|（中标）|（选）|)?(?:推荐)?(?:单位|供应商|供货商|服务商|商|人)(?:名称|)", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:中标|成交)(?:（成交）|（中标）|（选）|)?信息", SPS, 40), 2, MUT_WEIGHT],
         [Reg(POS_PRE, u"中标结果.{,10}第.包入围", SPS, 20), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"入围单位", SPS, 20), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"中标结果>>", SPS, 2), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"落标(?:单位|供应商|供货商|服务商|商|人)", SPS, 10), 0, MUT_WEIGHT]]},

    {"field_name": WINNING_COMPANY_ADDRESS,
     "elem_type": ELEM_TYPE_ADDRESS,
     "regulations": [
         [Reg(POS_PRE, u"地址", SPS, 10), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:中标|成交)(?:（成交）|（中标）|（选）|)?(?:推荐)?(?:单位|供应商|供货商|服务商|商|人)地址", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:中标|成交)(?:（成交）|（中标）|（选）|)?(?:推荐)?(?:单位|供应商|供货商|服务商|商|人)地址", SPS, 30), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:中标|成交)(?:（成交）|（中标）|（选）|)?信息", SPS, 40), 2, MUT_WEIGHT],
         [Reg(POS_PRE, u"落标(?:单位|供应商|供货商|服务商|商|人)", SPS, 10), 0, MUT_WEIGHT]]},

    {"field_name": WINNING_MONEY,
     "elem_type": ELEM_TYPE_MONEY,
     "regulations": [
         [Reg(POS_PRE, u"(?:金额|报价|总价|价格|单?价)", SPS, 20), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:中标|成交)(?:（成交）|（中标）|（选）|)?(?:金?额|报价|总价|价格|单?价)", SPS, 20), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:中标|成交)(?:（成交）|（中标）|（选）|)?信息", SPS, 30), 2, MUT_WEIGHT],
         [Reg(POS_PRE, u"总(?:中标|成交)(?:（成交）|（中标）|（选）|)?金?额", SPS, 20), 0, MUT_WEIGHT],
         [Reg(POS_PRE, u"最高限价", SPS, 10), 0, MUT_WEIGHT]]},

    {"field_name": CANDIDATE_COMPANY_NAME,
     "elem_type": ELEM_TYPE_COMPANY_NAME,
     "regulations": [
         [Reg(POS_PRE, u"(?:报价单位|报价人|供应商|供货商|服务商|投标人|投标单位)(?:名称|)", SPS, 10), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:中标|成交|)(?:（成交）|（中标）|（选）|)?(?:候选|侯选)(?:单位|供应商|供货商|服务商|商|人)(?:名称|)", SPS, 30), 1, ADD_WEIGHT],
         [Reg(POS_SUF, u"(?:报价单位|报价人|供应商|供货商|服务商|投标人|投标单位)(?:名称|)", SPS, 10), 0.5, ADD_WEIGHT],
         [Reg(POS_SUF, u"(?:中标|成交|)(?:（成交）|（中标）|（选）|)?(?:候选|侯选)(?:单位|供应商|供货商|服务商|商|人)(?:名称|)", SPS, 10), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:单位|供应商|供货商|服务商|商|人)名称", SPS, 10), 0.1, ADD_WEIGHT],
         [Reg(POS_PRE, u"落标(?:单位|供应商|供货商|服务商|商|人)", SPS, 10), 1., ADD_WEIGHT],
         [Reg(POS_PRE, u"地址|联系方式", SPS, 10), 0., MUT_WEIGHT]]},

    {"field_name": CANDIDATE_COMPANY_ADDRESS,
     "elem_type": ELEM_TYPE_ADDRESS,
     "regulations": [
         [Reg(POS_PRE, u"地址", SPS, 10), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:中标|成交|)(?:（成交）|（中标）|（选）|)?(?:候选|侯选)(?:单位|供应商|供货商|服务商|商|人)地址", SPS, 30), 1, ADD_WEIGHT]]},

    {"field_name": CANDIDATE_MONEY,
     "elem_type": ELEM_TYPE_MONEY,
     "regulations": [
         [Reg(POS_PRE, u"(?:金额|报价|总价|价格|单?价)", SPS, 20), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"投标(?:金?额|报价|总价|价格|单?价)", SPS, 20), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:中标|成交|)(?:（成交）|（中标）|（选）|)?(?:候选|侯选)(?:单位|供应商|供货商|服务商|商|人)", SPS, 20), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"总(?:中标|成交)(?:（成交）|（中标）|（选）|)?金额", SPS, 20), 0, MUT_WEIGHT],
         [Reg(POS_PRE, u"最高限价", SPS, 10), 0, MUT_WEIGHT]]},

    {"field_name": CANDIDATE_RANK,
     "elem_type": ELEM_TYPE_CANDIDATE_RANK,
     "regulations": [
         [Reg(POS_PRE, u"第", SPS, 2), 0.5, ADD_WEIGHT],
         [Reg(POS_SUF, u">>", SPS, 2), 0.5, ADD_WEIGHT],
         [Reg(POS_SUF, u"(?:中标|成交|)(?:（成交）|（中标）|（选）|)?(?:候选|侯选)(?:单位|供应商|供货商|服务商|商|人)|名", SPS, 2), 0.5, ADD_WEIGHT],
         [Reg(POS_PRE, u"排序|排名|名次", SPS, 4), 1, ADD_WEIGHT],
         [Reg(POS_PRE, u"(?:首|次)选", SPS, 0), 0.5, ADD_WEIGHT]]},
]



if __name__ == '__main__':
    Reg(POS_PRE, u"(?:采购|招标)公告(?:发布|)(?:日期|时间)", SPS, 10)

# SPS = u"，；。？！,;?!"
# regulations = [("announced_ts", "datetime",
#                 [["pref", u"招标公告日期[^%s]{,10}$" % SPS, 1, 0]]),
#
#                ("winning_ts", "datetime",
#                 [["pref", u"中标日期[^%s]{,10}$" % SPS, 1, 0]]),
#
#                ("deal_ts", "datetime",
#                 [["pref", u"成交日期[^%s]{,10}$" % SPS, 1, 0]]),
#
#                ("open_bid_ts", "datetime",
#                 [["pref", u"开标日期[^%s]{,10}$" % SPS, 1, 0]]),
#
#                ("evaluate_ts", "datetime",
#                 [["pref", u"(?:评标日期|评审日期)[^%s]{,10}$" % SPS, 1, 0]]),
#
#                ("end_bid_ts", "datetime",
#                 [["pref", u"结标日期[^%s]{,10}$" % SPS, 1, 0]]),
#
#                ("project_name", "usual_text",
#                 [["pref", u"项目名称[^%s]{,10}$" % SPS, 1, 0]]),
#
#                ("project_id", "usual_text",
#                 [["pref", u"项目编号[^%s]{,10}$" % SPS, 1, 0]]),
#
#                ("project_contact_name", "person_name",
#                 [["pref", u"(?:联系人|联系方式)[^%s]{,10}$" % SPS, 0.5, 0],
#                  ["pref", u"项目联系人|项目联系方式", u"[^，；。？！,;?!]", 12, 0.5, 0]]),
#
#                ("project_contact_phone", "phone_number",
#                 [["pref", u"联系电话|联系方式", u"[^，；。？！,;?!]", 10, 0.5, 0],
#                  ["pref", u"项目联系电话|项目联系方式", u"[^，；。？！,;?!]", 12, 0.5, 0]]),
#
#                ("project_type", "usual_text",
#                 [["pref", u"项目类型", u"[^，；。？！,;?!]", 10, 1, 0]]),
#
#                ("project_budget", "usual_text",
#                 [["pref", u"项目预算", u"[^，；。？！,;?!]", 10, 1, 0]]),
#
#                ("purchase_category", "usual_text",
#                 [["pref", u"采购品目|货物类型", u"[^，；。？！,;?!]", 10, 1, 0]]),
#
#                ("purchase_type", "usual_text",
#                 [["pref", u"采购类型|采购方式", u"[^，；。？！,;?!]", 10, 1, 0]]),
#
#                ("purchaser_name", "company_name",
#                 [["pref", u"采购人|采购单位", u"[^，；。？！,;?!]", 10, 1, 0]]),
#
#                ("purchaser_address", "address",
#                 [["pref", u"地址", u"[^，；。？！,;?!]", 10, 0.5, 0],
#                  ["pref", u"采购人地址", u"[^，；。？！,;?!]", 10, 0.5, 0]]),
#
#                ("purchaser_contact_name", "person_name",
#                 [["pref", u"联系人|联系方式", u"[^，；。？！,;?!]", 10, 0.5, 0],
#                  ["pref", u"采购联系人|采购人联系方式", u"[^，；。？！,;?!]", 10, 0.5, 0]]),
#
#                ("purchaser_contact_phone", "phone_number",
#                 [["pref", u"联系电话|联系方式", u"[^，；。？！,;?!]", 10, 0.5, 0],
#                  ["pref", u"采购联系电话|采购联系方式", u"[^，；。？！,;?!]", 10, 0.5, 0]]),
#
#                ("agent_name", "company_name",
#                 [["pref", u"采购代理机构", u"[^，；。？！,;?!]", 10, 1, 0]]),
#
#                ("agent_address", "address",
#                 [["pref", u"地址", u"[^，；。？！,;?!]", 10, 0.5, 0],
#                  ["pref", u"采购代理机构地址", u"[^，；。？！,;?!]", 10, 0.5, 0]]),
#
#                ("agent_contact_name", "person_name",
#                 [["pref", u"联系人|联系方式", u"[^，；。？！,;?!]", 10, 0.5, 0],
#                  ["pref", u"采购代理机构联系人|采购代理机构联系方式", u"[^，；。？！,;?!]", 10, 0.5, 0]]),
#
#                ("expert_names", "person_name",
#                 [["pref", u"谈判小组成员名单|评审委员会成员名单", u"[^，；。？！,;?!]", 10, 1, 0]]),
#
#                ("total_winning_money_amount", "money_amount",
#                 [["pref", u"总中标金额", u"[^，；。？！,;?!]", 10, 1, 0]]),
#
#                ("total_winning_money_unit", "money_unit",
#                 [["pref", u"总中标金额", u"[^，；。？！,;?!]", 10, 1, 0]]),
#
#                ("total_winning_money_currency", "money_currency",
#                 [["pref", u"总中标金额", u"[^，；。？！,;?!]", 10, 1, 0]]),
#
#                ("winning_company_name", "company_name",
#                 [["pref", u"(?:报价单位|供应商|供货商|服务商|投标人)(?:名称|)", u"[^，；。？！,;?!]", 10, 0.5, 0],
#                  ["pref", u"(?:中标|成交|中标（成交）|成交（中标）)(?:单位|供应商|供货商|服务商|商|人)(?:名称|)", u"[^，；。？！,;?!]", 10, 1, 0],
#                  ["pref", u"地址|联系方式", u"[^，；。？！,;?!]", 10, 0, 1]]),
#
#                ("winning_company_address", "address",
#                 [["pref", u"地址", u"[^，；。？！,;?!]", 10, 0.5, 0],
#                  ["pref", u"中标|成交", u"[^，；。？！,;?!]", 10, 0.5, 0]]),
#
#                ("winning_money_amount", "money_amount",
#                 [["pref", u"(?<!总)(?:中标|成交)金额", u"[^，；。？！,;?!]", 10, 1, 0]]),
#
#                ("winning_money_unit", "money_unit",
#                 [["pref", u"(?<!总)(?:中标|成交)金额", u"[^，；。？！,;?!]", 10, 1, 0]]),
#
#                ("winning_money_currency", "money_currency",
#                 [["pref", u"(?<!总)(?:中标|成交)金额", u"[^，；。？！,;?!]", 10, 1, 0]]),
#
#                ("candidate_company_name", "company_name",
#                 [["pref", u"(?:报价单位|供应商|供货商|服务商|投标人)(?:名称|)", u"[^，；。？！,;?!]", 10, 0.5, 0],
#                  ["pref", u"(?:中标|成交|中标（成交）|成交（中标）|)(?:候选|侯选)(?:单位|供应商|供货商|服务商|商|人)(?:名称|)", u"[^，；。？！,;?!]", 10, 1,
#                   0],
#                  ["pref", u"地址|联系方式", u"[^，；。？！,;?!]", 10, 0, 1]]),
#
#                ("candidate_company_address", "address",
#                 [["pref", u"地址", u"[^，；。？！,;?!]", 10, 0.5, 0],
#                  ["pref", u"中标|成交", u"[^，；。？！,;?!]", 10, 0.5, 0]]),
#
#                ("candidate_money_amount", "money_amount",
#                 [["pref", u"(?<!总)(?:中标|成交)金额", u"[^，；。？！,;?!]", 10, 1, 0]]),
#
#                ("candidate_money_unit", "money_unit",
#                 [["pref", u"(?<!总)(?:中标|成交)金额", u"[^，；。？！,;?!]", 10, 1, 0]]),
#
#                ("candidate_money_currency", "money_currency",
#                 [["pref", u"(?<!总)(?:中标|成交)金额", u"[^，；。？！,;?!]", 10, 1, 0]]),
#
#                ("candidate_rank", "number",
#                 [["pref", u"第", u"[^，；。？！,;?!]", 0, 0.5, 0],
#                  ["suff", u"(中标|成交)候选人", u"[^，；。？！,;?!]", 0, 0.5, 0],
#                  ["pref", u"排序|排名", u"[^，；。？！,;?!]", 10, 1, 0]]),
#                ]
