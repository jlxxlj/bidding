# coding=utf-8
# author="Jianghua Zhao"

import json
import os
import re
import requests
import sys

import util
from announce_attributes import *
from config.config import *
from result_template import *

if not USE_NER_SERVICE:
    from scu_ner.ner import ner_of_html

current_folder = os.path.dirname(os.path.abspath(__file__))
commonprefix = os.path.commonprefix

reload(sys)
sys.setdefaultencoding('utf-8')

# EXTRACT_ORG_API = 'http://192.168.31.116:29001/lp/api/lp?type=org'  # exact_entity
# EXTRACT_NAM_API = 'http://192.168.31.116:29001/lp/api/lp?type=name'
#
EXTRACT_ORG_API = "http://114.215.209.182:29000/lp/api/lp?type=org"
EXTRACT_NAM_API = "http://114.215.209.182:29000/lp/api/lp?type=name"
EXTRACT_INFO_SESSION = requests.session()
from config.config import NER_SERVICE_URL

SCU_NER_SESSION = requests.session()

if LOCAL_IP.startswith("172."):
    EXTRACT_ORG_API_ZW = "http://172.31.2.230:15559/nlp/entity/news"
else:
    EXTRACT_ORG_API_ZW = "http://54.223.48.232:15559/nlp/entity/news"
EXTRACT_INFO_ZW_SESSION = requests.session()

_cache = {}


def clear_cache():
    _cache.clear()


def _get_extract_entity_zw():
    if "extract_entity_zw" not in _cache:
        _cache["extract_entity_zw"] = {}
    return _cache["extract_entity_zw"]


# **************** 数据规范 **************** #
# **************** 数据规范 **************** #


def regulate_company_string(company_string):
    """
    规范化公司名称，将英文括号替换中文括号
    :param company_string:
    :return:
    """
    return company_string.replace(u"(", u"（").replace(u")", u"）")


def regulate_money(money_info):
    """
    规范化中标金额格式，
       将amount转换成float、unit转换成以元为单位
       将currency调整为 人民币,美元 等
    :param money_info:
    :return:
    """
    amount, unit, currency = money_info[MONEY_AMOUNT], money_info[MONEY_UNIT], money_info[MONEY_CURRENCY]

    if isinstance(amount, (str, unicode)) and len(amount) == 0:
        amount = None
    if isinstance(unit, (str, unicode)) and len(unit) == 0:
        unit = None
    if isinstance(currency, (str, unicode)) and len(currency) == 0:
        currency = None
    if amount is not None:
        if amount[0] in u"壹贰叁肆伍陆柒捌玖拾":
            amount = util.convert_cn_number(amount)
            unit = u"元"
            currency = u"人民币"
        else:
            amount = re.sub(u",|，", u"", amount)
            amount = float(amount)
            if unit is not None and unit[0] in util.DICT_CN_COMPLEX_NUMBER:
                amount *= util.DICT_CN_COMPLEX_NUMBER.get(unit[0])
                unit = unit[1:]
    if currency is not None:
        if currency in (u"人民币", u"￥", u'¥', u"RMB", u"CNY"):
            currency = u"人民币"
        elif currency in (u"美元", u"$", u"USD"):
            currency = u"美元"
        elif currency in (u"欧元", u"€", u"EUR"):
            currency = u"欧元"
    else:
        if amount and unit:
            currency = u"人民币"

    if unit is None and amount and currency:
        if currency == u"人民币":
            unit = u"元"
        elif currency == u"美元":
            unit = u"美元"
        elif currency == u"欧元":
            unit = u"欧元"

    res = {
        MONEY_AMOUNT: amount,
        MONEY_UNIT: unit,
        MONEY_CURRENCY: currency
    }

    return res


def regulate_time_string(time_string):
    """
    # 规范化中标时间格式
    :param time_string:
    :return:
    """
    dt = None

    if len(time_string) > 0:
        y, m, d = re.split(u"年|月|日|\.|-|/", time_string)[:3]
        dict_cn_number_year = dict([(x, 0) for x in u"○〇ＯО0oO"])
        dict_cn_number_year.update(util.DICT_CN_SIMPLE_NUMBER)
        if y[0] in dict_cn_number_year:
            t = ""
            for w in y:
                t += str(int(dict_cn_number_year.get(w)))
            y = t
        if m[0] in util.DICT_CN_SIMPLE_NUMBER:
            m = str(int(util.convert_cn_number(m)))
        if d[0] in util.DICT_CN_SIMPLE_NUMBER:
            d = str(int(util.convert_cn_number(d)))

        try:
            dt = datetime.date(year=int(y), month=int(m), day=int(d))
            dt = dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    return dt


def regulate_number_string(number_string):
    number = None

    if len(number_string) > 0:
        try:
            if number_string[0] in util.DICT_CN_SIMPLE_NUMBER:
                number = int(util.convert_cn_number(number_string))
            else:
                number = int(number_string)
        except ValueError:
            pass

    return number


def regulate_candidate_rank(rank_string):
    if rank_string == u"首选":
        number = 1
    elif rank_string == u"次选":
        number = 2
    else:
        number = regulate_number_string(rank_string)
    return number


def regulate_project_id(project_id_string):
    project_id_string = project_id_string.upper()
    project_id_string = project_id_string.replace(u"(", u"（")
    project_id_string = project_id_string.replace(u")", u"）")
    project_id_string = project_id_string.replace(u"[", u"【")
    project_id_string = project_id_string.replace(u"]", u"】")
    project_id_string = util.strQ2B(project_id_string)
    return project_id_string


# **************** 数据规范 **************** #
# **************** 数据规范 **************** #


# **************** 信息元抽取方法 **************** #
# **************** 信息元抽取方法 **************** #

def _get_company_name_use_crf_ner(content):
    data = EXTRACT_INFO_SESSION.post(url=EXTRACT_ORG_API, data=json.dumps({'content': content}),
                                     headers={'Content-Type': 'application/json;charset=utf8'})
    return data.json()['results'] if data.ok else []


def _get_company_name_use_scu_ner(content):
    if not USE_NER_SERVICE:
        return ner_of_html(content)

    data_n = SCU_NER_SESSION.post(url=NER_SERVICE_URL, data=json.dumps({'content': content}),
                                  headers={'Content-Type': 'application/json;charset=utf8'},
                                  timeout=120)
    return data_n.json()['results'] if data_n.ok else []


def _get_company_name_use_crf_ner_zw(content):
    extract_entity_zw = _get_extract_entity_zw()
    hash_code = hash(content)
    if hash_code not in extract_entity_zw:
        params = {"sentence": content, "confidence": 0.8}
        data_n = EXTRACT_INFO_ZW_SESSION.post(url=EXTRACT_ORG_API_ZW, data=json.dumps(params),
                                              headers={'Content-Type': 'application/json;charset=utf8'},
                                              timeout=60)
        if data_n.status_code == 200:
            try:
                data = data_n.json()
                extract_entity_zw[hash_code] = data
            except Exception as e:
                print e
    return extract_entity_zw.get(hash_code, {}).get("company", []) + extract_entity_zw.get(hash_code, {}).get("org", [])


def _get_person_name_use_crf_ner(content):
    data = EXTRACT_INFO_SESSION.post(url=EXTRACT_NAM_API, data=json.dumps({'content': content}),
                                     headers={'Content-Type': 'application/json;charset=utf8'})
    return data.json()['results'] if data.ok else []


def _get_person_name_use_crf_ner_zw(content):
    extract_entity_zw = _get_extract_entity_zw()
    hash_code = hash(content)
    if hash_code not in extract_entity_zw:
        params = {"sentence": content, "confidence": 0.8}
        data_n = EXTRACT_INFO_ZW_SESSION.post(url=EXTRACT_ORG_API_ZW, data=json.dumps(params),
                                              headers={'Content-Type': 'application/json;charset=utf8'},
                                              timeout=60)
        if data_n.status_code == 200:
            try:
                data = data_n.json()
                extract_entity_zw[hash_code] = data
            except Exception as e:
                print e
    return extract_entity_zw.get(hash_code, {}).get("person", [])


def obtain_company_name(input_data, with_context=False, src_html=None):
    """
    组织名称抽取
    :param input_data:
    :param with_context:
    :param src_html:
    :return:
    """
    if isinstance(input_data, str):
        input_data = unicode(input_data)
    if isinstance(src_html, str):
        src_html = unicode(src_html)

    max_len = 10000
    company_names = []
    stop_char = u"\n。！；，"

    st = 0
    while st < len(input_data):
        idx = st + max_len
        for cha in stop_char:
            t = input_data.find(cha, st + int(max_len / 2))
            if t > 0:
                idx = t
                break
        text = input_data[st: idx]
        st = idx
        try:
            company_names += _get_company_name_use_crf_ner_zw(text)
        except:
            pass

    # company_names += ner_of_html(input_data)

    company_names += _get_company_name_use_scu_ner(input_data)

    if src_html is not None:
        company_names += _get_company_name_use_scu_ner(src_html)
    company_names = list(set(company_names))

    # 去掉抽取的公司简称
    name_pos = []
    for name in company_names:
        st, rep = 0, False
        while st >= 0:
            idx = input_data.find(name, st)
            if idx >= 0:
                st = idx + len(name)
                name_pos.append((name, idx, st))
            elif st == 0 and rep is False:
                rep = True
                name = name.replace(u"(", u"（").replace(u")", u"）")
            else:
                st = -1
    name_pos = sorted(name_pos, key=lambda x: x[1])
    delete_idx = []
    for i, nmp in enumerate(name_pos):
        for j, nmp_ in enumerate(name_pos):
            if i != j and (j not in delete_idx) and (
                                nmp_[1] < nmp[1] < nmp_[2] or (nmp_[1] == nmp[1] and nmp_[2] >= nmp[2])):
                delete_idx.append(i)
    company_names = [name_pos[i][0] for i in range(len(name_pos)) if i not in delete_idx]

    # 根据规则筛选
    tmp = []
    for com_nm in company_names:
        com_nm = re.sub(u"^名称", u"", com_nm)
        if com_nm.endswith(u"采购单位"):
            continue
        tmp.append(com_nm)
    company_names = tmp

    if not with_context:
        return company_names
    else:
        return company_names, util.split_text_by_strings(company_names, input_data)


def obtain_complex_company_name(input_data, with_context=False, src_html=None):
    company_names = obtain_company_name(input_data, src_html=src_html)

    # 分公司情况
    name_pos = []
    st = 0
    for cpy in company_names:
        idx = input_data.find(cpy, st)
        name_pos.append((cpy, idx))
        st = idx + len(cpy)
    name_pos = sorted(name_pos, key=lambda x: x[1])
    company_names = []
    for i, (name, pos) in enumerate(name_pos):
        pre_name, pre_pos = name_pos[i - 1]
        if i > 0 and pos == pre_pos + len(pre_name) and name.endswith(u"分公司"):
            company_names[-1] += name
        else:
            company_names.append(name)

    # 联合体情况

    if not with_context:
        return company_names
    else:
        return company_names, util.split_text_by_strings(company_names, input_data)


def obtain_datetime(input_data, with_context=False):
    """
    日期抽取
    :param input_data:
    :param with_context:
    :return:
    """
    if isinstance(input_data, str):
        input_data = unicode(input_data)

    cn_number = u"[零一二三四五六七八九十○〇ＯО0oO]"
    cn_time_ptn = u"二%s{3}年%s{1,3}月%s{1,3}日" % (cn_number, cn_number, cn_number)
    ot_time_ptn = u"2\d{3}年\d{1,2}月\d{1,2}日|2\d{3}-\d{1,2}-\d{1,2}|2\d{3}\.\d{1,2}\.\d{1,2}|2\d{3}/\d{1,2}/\d{1,2}"

    re_time = re.compile(cn_time_ptn + u"|" + ot_time_ptn)
    time_strings = re_time.findall(input_data)
    time_strings = [t for t in time_strings if regulate_time_string(t) is not None]

    if not with_context:
        return time_strings
    else:
        return time_strings, util.split_text_by_strings(time_strings, input_data)


def obtain_money_amount(input_data, with_context=False):
    """
    抽取金额数字
    :param input_data:
    :param with_context:
    :return:
    """
    if isinstance(input_data, str):
        input_data = unicode(input_data)

    cn_number = u"零壹贰叁肆伍陆柒捌玖拾"
    cn_money_pattern = u"[%s][%s佰仟百千万亿]*[元圆](?:整|[%s]+角[%s]+分|[%s]+角|[%s]+分)" % (
        cn_number[1:], cn_number, cn_number[:-1], cn_number[:-1], cn_number[:-1], cn_number[:-1])
    money_pattern = u"\d+(?:[,，]\d{3})*(?:\.\d+)?(?=$|\s|[\(（]?[十百千万亿]?美?元?)"
    re_amount = re.compile(cn_money_pattern + "|" + money_pattern)
    amount_strings = re_amount.findall(input_data)

    if not with_context:
        return amount_strings
    else:
        return amount_strings, util.split_text_by_strings(amount_strings, input_data)


def obtain_money_currency(input_data, with_context=False):
    """
    抽取金额币种
    :param input_data:
    :param with_context:
    :return:
    """
    if isinstance(input_data, str):
        input_data = unicode(input_data)

    re_currency = re.compile(u"人民币|美元|欧元|￥|¥|\$|€|RMB|CNY|USD|EUR")
    currency_strings = re_currency.findall(input_data)

    if not with_context:
        return currency_strings
    else:
        return currency_strings, util.split_text_by_strings(currency_strings, input_data)


def obtain_money_unit(input_data, with_context=False):
    """
    抽取金额单位
    :param input_data:
    :param with_context:
    :return:
    """
    if isinstance(input_data, str):
        input_data = unicode(input_data)

    quantifier = u"[\u4e00-\u9fa5]+"
    with open(os.path.join(current_folder, "toolkit/quantifier.txt"), "r") as f:
        quantifier = f.readline().strip()
        quantifier = unicode(quantifier)
        quantifier = u"每?[半%s]?(?:%s)" % (u"一二三四五六七八九十百千壹贰叁肆伍陆柒捌玖拾佰仟万亿", quantifier)
    unit = u"(?:百|千|万|百万|千万|亿)?[美欧日]?元(?:[/∕/](?:%s)+)?" % quantifier
    unit_strings = re.findall(unit, input_data)

    if not with_context:
        return unit_strings
    else:
        return unit_strings, util.split_text_by_strings(unit_strings, input_data)


def obtain_money(input_data, with_context=False):
    """
    抽取金额
    :param input_data:
    :param with_context:
    :return:
    """
    res, contexts = [], []

    amount_strings = obtain_money_amount(input_data)
    texts = util.split_text_by_strings(amount_strings, input_data)
    for i in range(len(amount_strings)):
        amount = amount_strings[i]

        pre_context, suf_context = texts[i][0], texts[i][1]
        is_complex = (amount[0] in u"零壹贰叁肆伍陆柒捌玖拾")
        unit = None
        if not is_complex:
            unit_strings, cxt = obtain_money_unit(texts[i][1], with_context=True)
            if len(unit_strings) > 0:
                idx = texts[i][1].find(unit_strings[0])
                inter = texts[i][1][:idx]

                is_in_complex = False
                if len(cxt[0][0]) > 0:
                    is_in_complex = cxt[0][0][-1] in u"一二三四五六七八九十百千壹贰叁肆伍陆柒捌玖拾佰仟万亿"

                if len(inter) < 5 and re.search(u"\n", inter) is None and is_in_complex is False:
                    unit = unit_strings[0]
                    if len(texts[i][1][idx + len(unit):]) < len(suf_context):
                        suf_context = texts[i][1][idx + len(unit):]
        if not unit and not is_complex and "table" in pre_context:
            unit_strings, cxt = obtain_money_unit(texts[i][0], with_context=True)
            if len(unit_strings) > 0:
                idx = texts[i][0].rfind(unit_strings[-1])
                inter = texts[i][0][idx + len(unit_strings[-1]):]

                is_in_complex = False
                if len(cxt[0][0]) > 0:
                    is_in_complex = cxt[0][0][-1] in u"一二三四五六七八九十百千壹贰叁肆伍陆柒捌玖拾佰仟万亿"

                if len(inter) < 8 and re.search(u"\n", inter) is None and is_in_complex is False:
                    unit = unit_strings[-1]
                    if len(texts[i][0][:idx]) < len(pre_context):
                        pre_context = texts[i][0][:idx]

        currency = None
        currency_strings = obtain_money_currency(texts[i][0])
        if len(currency_strings) > 0:
            idx = texts[i][0].rfind(currency_strings[-1])
            inter = texts[i][0][idx + len(currency_strings[-1]):]
            if len(inter) < 10 and re.search(u"\n", inter) is None:
                currency = currency_strings[-1]
                if len(texts[i][0][:idx]) < len(pre_context):
                    pre_context = texts[i][0][:idx]
        if not currency:
            currency_strings = obtain_money_currency(texts[i][1])
            if len(currency_strings) > 0:
                idx = texts[i][1].find(currency_strings[0])
                inter = texts[i][1][:idx]
                if len(inter) < 5 and re.search(u"\n", inter) is None:
                    currency = currency_strings[0]
                    if len(texts[i][1][idx + len(currency):]) < len(suf_context):
                        suf_context = texts[i][1][idx + len(currency):]

        if unit is None and currency is None:
            if re.match(u"[千|万|亿](?:$|\s+)", texts[i][1]):
                unit = texts[i][1][0] + u"元"
            if (len(texts[i][1]) == 0 or re.match(u"\s+", texts[i][1])) and re.match("\d+\.\d{6}", amount) and float(
                    amount) < 100000.:
                unit = u"万元"

        if unit or currency or amount[0] in u"零壹贰叁肆伍陆柒捌玖拾":
            money = money_template()
            money[MONEY_AMOUNT] = amount
            money[MONEY_UNIT] = unit
            money[MONEY_CURRENCY] = currency
            res.append(money)
            contexts.append([pre_context, suf_context])

    # 去掉大写金额与小写金额相同的金额
    if len(res) > 1:
        rep_idx = []
        pre_money = regulate_money(res[0])
        for i in range(1, len(res)):
            r_money = regulate_money(res[i])
            pre = res[i - 1][MONEY_AMOUNT][0] in u"零壹贰叁肆伍陆柒捌玖拾"
            cur = res[i][MONEY_AMOUNT][0] in u"零壹贰叁肆伍陆柒捌玖拾"
            if pre_money[MONEY_AMOUNT] == r_money[MONEY_AMOUNT] and pre != cur:
                rep_idx.append(i)
                # if pre is True:
                #     rep_idx.append(i)
                # else:
                #     rep_idx.append(i - 1)
            pre_money = r_money
        res = [res[i] for i in range(len(res)) if i not in rep_idx]
        contexts = [contexts[i] for i in range(len(contexts)) if i not in rep_idx]

    if not with_context:
        return res
    else:
        return res, contexts


def obtain_person_name(input_data, with_context=False):
    """
    抽取人名
    :param input_data:
    :param with_context:
    :return:
    """
    max_len = 10000
    name_strings = []
    stop_char = u"\n。！；，"

    st = 0
    while st < len(input_data):
        idx = st + max_len
        for cha in stop_char:
            t = input_data.find(cha, st + int(max_len / 2))
            if t > 0:
                idx = t
                break
        text = input_data[st: idx]
        st = idx
        try:
            name_strings = _get_person_name_use_crf_ner_zw(text)
        except Exception as e:
            name_strings = []

    if not with_context:
        return name_strings
    else:
        return name_strings, util.split_text_by_strings(name_strings, input_data)


def obtain_phone_number(input_data, with_context=False):
    """
    联系电话抽取
    :param input_data:
    :param with_context:
    :return:
    """
    if isinstance(input_data, str):
        input_data = unicode(input_data)

    re_phone_number = re.compile(
        "((?:\d{4}|\d{3})-(?:\d{7,8})-(?:\d{4}|\d{3}|\d{2}|\d{1})|(?:\d{11})|(?:\d{7,8})|(?:\d{4}|\d{3})-(?:\d{7,8})|(?:\d{7,8})-(?:\d{4}|\d{3}|\d{2}|\d{1}))")
    phone_strings = re_phone_number.findall(input_data)

    if not with_context:
        return phone_strings
    else:
        return phone_strings, util.split_text_by_strings(phone_strings, input_data)


def obtain_address(input_data, with_context=False):
    """
    地址抽取
    :param input_data:
    :param with_context:
    :return:
    """
    if isinstance(input_data, str):
        input_data = unicode(input_data)

    loc = [u"县", u"区", u"乡", u"镇", u"村", u"社", u"组", u"街", u"路"]
    dtl = [u"号", u"楼", u"栋", u"单元", u"层", u"室"]
    with open(os.path.join(current_folder, "toolkit/prov.txt"), "r") as f:
        lines = f.readlines()
        prov = "|".join([line.strip() for line in lines])
    with open(os.path.join(current_folder, "toolkit/city.txt"), "r") as f:
        lines = f.readlines()
        city = "|".join([line.strip() for line in lines])
    aa = ""
    for t in loc:
        aa += u"(?:[\u4e00-\u9fa5]{,20}%s)?" % t
    bb = ""
    for t in dtl:
        bb += u"(?:[\-a-zA-Z0-9\u4e00-\u9fa5]{,30}%s)?" % t

    re_address = u"(?:%s)?(?:%s)" % (prov, city) + aa + bb
    re_address = re.compile(re_address)
    address_strings = re_address.findall(input_data)

    if not with_context:
        return address_strings
    else:
        return address_strings, util.split_text_by_strings(address_strings, input_data)


def obtain_usual_text(input_data, with_context=False):
    """
    一段寻常文本抽取
    :param input_data:
    :param with_context:
    :return:
    """
    if isinstance(input_data, str):
        input_data = unicode(input_data)

    re_usual_text = re.compile(u"[^，；。？！,;?!>\n]+")
    if len(input_data) > 5000:
        text_strings = re_usual_text.findall(input_data[:5000])
    else:
        text_strings = re_usual_text.findall(input_data)

    # 删除单括号的情况
    def delete_redundant_suffix(sentence):
        stack = [(0, 0)]
        for i, char in enumerate(sentence):
            if char in u"(（":
                stack.append((i, 1))
            elif char in u")）":
                if stack[-1][1] - 1 == 0:
                    stack.pop()
                else:
                    stack.append((i, -1))
                    break
        if len(stack) > 1:
            return sentence[:stack[1][0]]
        return sentence

    for idx, text in enumerate(text_strings):
        text_strings[idx] = delete_redundant_suffix(text)

    if not with_context:
        return text_strings
    else:
        return text_strings, util.split_text_by_strings(text_strings, input_data)


def obtain_number(input_data, with_context=False):
    """
    抽取数字
    :param input_data:
    :param with_context:
    :return:
    """
    if isinstance(input_data, str):
        input_data = unicode(input_data)

    re_number = re.compile(u"[一二三四五六七八九十]+|[1-9]\d*")
    number_strings = re_number.findall(input_data)

    if not with_context:
        return number_strings
    else:
        return number_strings, util.split_text_by_strings(number_strings, input_data)


def obtain_candidate_rank(input_data, with_context=False):
    """
    抽取候选排序
    :param input_data:
    :param with_context:
    :return:
    """
    if isinstance(input_data, str):
        input_data = unicode(input_data)

    re_number = re.compile(u"[一二三四五六七八九十]+|[1-9]\d*|(?:首|次)选")
    number_strings = re_number.findall(input_data)
    number_strings = [x for x in number_strings if regulate_candidate_rank(x) <= 100]

    if not with_context:
        return number_strings
    else:
        contexts = util.split_text_by_strings(number_strings, input_data)
        for i, string in enumerate(number_strings):
            if re.search(u"(?:首|次)选", string):
                contexts[i] = (contexts[i][0] + string, contexts[i][1])
        return number_strings, contexts


def obtain_role_name(input_data, with_context=False):
    """
    抽取组织实体在项目中扮演的角色
    :param input_data:
    :param with_context:
    :return:
    """
    t = u"(?:拟|首选|第[一二三四五六七八九十]|推荐)?"
    role_reg = re.compile(
        u"%s(?:中标|成交|入围)(?:（成交）|（中标）|（选）|)?(?:候选|侯选|推荐)?(?:单位|供应商|供货商|服务商|商|人)|(?:报价单位|供应商|供货商|服务商|投标人)" % t)
    role_name = role_reg.findall(input_data)

    if not with_context:
        return role_name
    else:
        return role_name, util.split_text_by_strings(role_name, input_data)


def obtain_project_id(input_data, with_context=False):
    """
    抽取项目编号
    :param input_data:
    :param with_context:
    :return:
    """
    re_id_char = re.compile(u"[0-9A-Za-z]")
    # re_parentheses = re.compile(u"[\(（][^\(（\)）]*[\)）]")
    # re_redundant_suffix = re.compile(u"[\)）].*$")
    project_id = obtain_usual_text(input_data=input_data)
    project_id = [x for x in project_id if re_id_char.search(x)]
    # for idx, pid in enumerate(project_id):
    #     while re_parentheses.search(pid):
    #         pid = re_parentheses.sub(u"", pid)
    #     redundant_suffix = re_redundant_suffix.findall(pid)
    #     if len(redundant_suffix) > 0:
    #         project_id[idx] = project_id[idx].replace(redundant_suffix[0], u"")

    if not with_context:
        return project_id
    else:
        return project_id, util.split_text_by_strings(project_id, input_data)


def element_obtain_regular_func_table():
    table = {
        ELEM_TYPE_COMPANY_NAME: (obtain_complex_company_name, regulate_company_string),
        ELEM_TYPE_DATETIME: (obtain_datetime, regulate_time_string),
        ELEM_TYPE_MONEY: (obtain_money, regulate_money),
        ELEM_TYPE_PERSON_NAME: (obtain_person_name, None),
        ELEM_TYPE_PHONE_NUMBER: (obtain_phone_number, None),
        ELEM_TYPE_ADDRESS: (obtain_address, None),
        ELEM_TYPE_USUAL_TEXT: (obtain_usual_text, None),
        # ELEM_TYPE_NUMBER: (obtain_number, regulate_number_string),
        ELEM_TYPE_CANDIDATE_RANK: (obtain_candidate_rank, regulate_candidate_rank),
        ELEM_TYPE_ROLE_NAME: (obtain_role_name, None),
        ELEM_TYPE_PROJECT_ID: (obtain_project_id, regulate_project_id),
    }
    return table

# **************** 信息元抽取方法 **************** #
# **************** 信息元抽取方法 **************** #
