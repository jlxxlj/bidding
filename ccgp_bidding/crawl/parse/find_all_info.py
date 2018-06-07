# -*- coding: utf-8 -*-
# __author__ = 'Jianghua Zhao'
# jianghua.zhao@socialcredits.cn

import re
import requests
import json
import util
import numpy as np
import datetime

from conf.config import EXTRACT_ENTITY_API


def obtain_company_name(input_data):
    data = requests.post(url=EXTRACT_ENTITY_API, data=json.dumps({'content': input_data}),
                         headers={'Content-Type': 'application/json;charset=utf8'})
    return data.json()['results'] if data.ok else []


def split_text_by_strings(strings, text):
    """
    将text按strings里的字符串依次分段
    :param strings: list 用于分割的字符串，必须依次出现在原字符串中，可以为空
    :param text: str 待分割字符串
    :return: list 返回分段结果
    """
    result = []
    suffix_text = text
    count = 0
    for string in strings:
        ind = suffix_text.find(string)
        if ind >= 0:
            count += ind
            suffix_text = suffix_text[ind + len(string):]
            result.append((text[:count], suffix_text))
            count += len(string)
        else:
            msg = "Call function split_text_by_strings error: " + \
                  "There is no substring '%s' in '%s', please check your inputs." % (string, text)
            raise Exception(msg)
    return result


def regular_money(money_info):
    """
    # 规范化中标金额格式
    :param money_info:
    :return:
    """
    money, unit = money_info["money"], money_info["unit"]
    if isinstance(unit, (str, unicode)) and len(unit)==0:
        unit = None
    if isinstance(money, (str, unicode)) and len(money) == 0:
        money = None
    if money is not None:
        if money[0] in u"壹贰叁肆伍陆柒捌玖拾":
            money = util.convert_cn_number(money)
        else:
            money = re.sub(u",|，", u"", money)
            money = float(money)
            if unit is not None and unit[0] in util.DICT_CN_COMPLEX_NUMBER:
                money *= util.DICT_CN_COMPLEX_NUMBER.get(unit[0])
                unit = unit[1:]
    money_info["money"] = money
    money_info["unit"] = unit
    return money_info


def regular_time(time):
    """
    # 规范化中标时间格式
    :param time:
    :return:
    """
    if len(time) > 0:
        y, m, d = re.split(u"年|月|日|\.|-", time)[:3]
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
            time = datetime.date(year=int(y), month=int(m), day=int(d))
            time = time.strftime("%Y-%m-%d")
        except ValueError, e:
            # print "ValueError:", time
            return None
    return time


def find_valid_time(text):
    number = u"[零一二三四五六七八九十○〇ＯО0oO]"
    time_pattern = u'二%s{3}年%s{1,3}月%s{1,3}日|2\d{3}年\d{1,2}月\d{1,2}日|2\d{3}-\d{1,2}-\d{1,2}|2\d{3}\.\d{1,2}\.\d{1,2}' % (
        number, number, number)
    re_time = re.compile(time_pattern)
    time_strings = re_time.findall(text)
    time_strings = [t for t in time_strings if regular_time(t) is not None]

    return time_strings


def get_bid_time(text):
    """
    获取文本中的日期字符串，以及这个字符串是中标日期的优先级
    :param text:
    :return:
    """
    text = text.replace(u' ', u'')
    text = re.sub(u"\s*", u"", text)

    time_strings = find_valid_time(text)
    texts = split_text_by_strings(time_strings, text)

    result = []
    for i in range(len(time_strings)):
        priority = 0
        pattern = u"(?:开标)[^，；。？！,;?!]+"  # 时间字符串有 "日期|时间" 字符串前有限定语 "开标|中标|招标|成交|定标"
        if re.search(pattern, texts[i][0]) is not None:
            priority += 1
        pattern = u"[^，；。？！,;?!]+(?:开标)"  # 时间字符串有 "日期|时间" 字符串前有限定语 "开标|中标|招标|成交|定标"
        if re.search(pattern, texts[i][1]) is not None:
            priority += 1

        pattern = u"(?:评审)[^，；。？！,;?!]+"  # 时间字符串有 "日期|时间" 字符串前有限定语 "开标|中标|招标|成交|定标"
        if re.search(pattern, texts[i][0]) is not None:
            priority += 2
        pattern = u"[^，；。？！,;?!]+(?:评审)"  # 时间字符串有 "日期|时间" 字符串前有限定语 "开标|中标|招标|成交|定标"
        if re.search(pattern, texts[i][1]) is not None:
            priority += 2

        pattern = u"(?:中标|成交|定标|确定)[^，；。？！,;?!]+"  # 时间字符串有 "日期|时间" 字符串前有限定语 "开标|中标|招标|成交|定标"
        if re.search(pattern, texts[i][0]) is not None:
            priority += 4
        pattern = u"[^，；。？！,;?!]+(?:中标|成交|定标|确定)"  # 时间字符串有 "日期|时间" 字符串前有限定语 "开标|中标|招标|成交|定标"
        if re.search(pattern, texts[i][1]) is not None:
            priority += 4

        pattern = u"(?:招标|公告发布)[^，；。？！,;?!]*"  # 时间前面有招标等关键字
        if re.search(pattern, texts[i][0]) is not None:
            priority -= 8
        pattern = u"[^，；。？！,;?!]*(?:招标|公告发布)"  # 时间前面有招标等关键字
        if re.search(pattern, texts[i][1]) is not None:
            priority -= 8

        pre_pattern = u"(?:日期|时间)[^，；。？！,;?!]{,5}"  # 时间字符串最多间隔10个字符有前缀 "日期|时间"
        if re.search(pre_pattern, texts[i][0]) is not None:
            priority *= 2

        # 如果是在中标信息段落下的情况
        pattern = u"(?:中标|成交)(?:信息|情况)>>"
        if re.search(pattern, text) is not None:
            priority *= 2

        time_info = {"priority": priority, "inline_pos": i, "time": time_strings[i]}
        result.append(time_info)
    return result


def find_valid_company_name(text):
    """
    find all valid company name in text
    :param text:
    :return:
    """
    company_suffix = [u"公司", u"厂", u"院", u"所", u"中心", u"汽贸", u"集团", u"店", u"行"]
    for suff in company_suffix:
        company_pattern = u"[a~zA~Z\u4e00-\u9fa5（）\(\)]{4,40}(?:%s)" % suff
        company_strings = re.findall(company_pattern, text)
        if len(company_strings) > 0:
            break
    company_strings = [string for string in company_strings if util.is_company_name(string)]

    # 利用实体识别将粗略抽取的公司名称再进行抽取
    texts = split_text_by_strings(company_strings, text)
    for i in range(len(company_strings)):
        com_str = company_strings[i]
        # 删除已知的一些关键字
        pattern = u"(?:中标|成交|投标|竞标|)(?:候选|侯选|)(?:单位|供应商|供货商|中标商|成交商|人)(?:名称|)(?:为|是|)|" + \
            u"(?:一致|)推荐(?:第.+名|)(?:.+的|.+为|.+是|)|" + \
            u"[A-Z一二三四五六七八九十]+(?:包|分标|标段)(?:）|\)|)|" + \
            u"一致评定|^（.*）|^\(.*\)"
        strs = re.findall(pattern, com_str)
        strs = [x for x in strs if len(x) >= 3]   # 保证不会因为关键字太短出现错误检测
        contxt = split_text_by_strings(strs, com_str)
        tmp_str = com_str
        for j in range(len(strs)):
            if len(contxt[j][1]) < len(tmp_str):
                tmp_str = contxt[j][1]
        com_str = tmp_str
        # 如果这是一个自然分段就跳过实体识别
        if len(texts[i][0]) > 1 and texts[i][0][-2:] == u">>":
            company_strings[i] = com_str
            continue

        # 调用在线实体识别API
        try:
            entities = obtain_company_name(com_str)
        except Exception, e:
            print e.message
            break

        if len(entities) <= 0:
            company_strings[i] = ""
        else:
            marks = np.zeros(len(com_str))
            for ent in entities:
                ind = com_str.find(ent)
                marks[ind:ind + len(ent)] += 1
            ind = 0
            for j in range(1, len(com_str)):
                if marks[j - 1] < 1 <= marks[j]:
                    ind = j
            company_strings[i] = com_str[ind:]
    # 保证公司名称最少不少于4个字
    company_strings = [x for x in company_strings if len(x) >= 4]
    return company_strings


def get_bid_company(text):
    """
    获取文本中的公司名字符串，以及这个字符串是中标公司的优先级
    :param text:
    :return:
    """
    company_strings = find_valid_company_name(text)
    texts = split_text_by_strings(company_strings, text)
    texts = [(re.sub(u" |\s+", u"", t[0]), re.sub(u" |\s+", u"", t[1])) for t in texts]

    result = []
    for i in range(len(company_strings)):
        priority, level = 0, 0
        # 确定是中标单位的正向信息
        # pattern = u"(?:中标单位|供应商|中标人|中标商|供货商|中标候选人|成交单位|中选单位).{1,10}$"
        pattern = u"(?:中标|成交)(?:单位|供应商|供货商|商|人)(?:名称|)>>$"  # 直接指出是中标公司的情况
        if re.search(pattern, texts[i][0]) is not None:
            level = 2
        pattern = u"(?:中标|成交|)(?:候选|侯选)(?:单位|供应商|供货商|商|人)(?:名称|)>>$"  # 中标候选单位
        if re.search(pattern, texts[i][0]) is not None:
            level = 1

        candidate_pattern_0 = u"预(?:中标|成交|中标（成交）|成交（中标）)(?:单位|供应商|供货商|服务商|商|人)(?:名称|)(?!地址|联系方式)"
        winning_pattern = u"(?:中标|成交|中标（成交）|成交（中标）)(?:单位|供应商|供货商|服务商|商|人)(?:名称|)(?!地址|联系方式)"
        candidate_pattern_1 = u"(?:中标|成交|中标（成交）|成交（中标）|)(?:候选|侯选)(?:单位|供应商|供货商|服务商|商|人)(?:名称|)(?!地址|联系方式)"
        part_pattern = u"(?:报价单位|供应商|供货商|服务商|投标人)(?:名称|)(?!地址|联系方式)"
        if re.search(candidate_pattern_0 + u"[^，；。？!]{0,10}$", texts[i][0]) is not None:
            priority += 8
        elif re.match(u"[^，；。？!]{0,10}" + candidate_pattern_0, texts[i][1]) is not None:
            priority += 8
        elif re.search(winning_pattern + u"[^，；。？!]{0,10}$", texts[i][0]) is not None:
            priority += 16
        elif re.match(u"[^，；。？!]{0,10}" + winning_pattern, texts[i][1]) is not None:
            priority += 16
        elif re.search(candidate_pattern_1 + u"[^，；。？!]{0,10}$", texts[i][0]) is not None:
            priority += 8
        elif re.match(u"[^，；。？!]{0,10}" + candidate_pattern_1, texts[i][1]) is not None:
            priority += 8
        elif re.search(part_pattern + u"[^，；。？!]{0,10}$", texts[i][0]) is not None:
            priority += 4
        elif re.match(u"[^，；。？!]{0,10}" + part_pattern, texts[i][1]) is not None:
            priority += 4

        # pattern = u"(?:中标|成交)(?:单位|供应商|供货商|商|人)(?:名称|)(?!地址|联系方式).{1,10}$"  # 直接指出是中标公司的情况
        # if re.search(pattern, texts[i][0]) is not None:
        #     priority += 16
        # pattern = u"(?:中标|成交|)候选(?:单位|供应商|供货商|商|人).{1,10}$"  # 中标候选单位
        # if re.search(pattern, texts[i][0]) is not None:
        #     priority += 8
        # pattern = u"(?:报价单位|供应商|供货商|投标人).{1,10}$"  # 公司字符串前最多间隔15个字符有前缀 "中标单位|供应商|中标人|供货商"
        # if re.search(pattern, texts[i][0]) is not None:
        #     priority += 4
        # pattern = u"(?:单位|商).{1,10}$"  # 公司字符串前最多间隔15个字符有前缀 "中标单位|供应商|中标人|供货商"
        # if re.search(pattern, texts[i][0]) is not None:
        #     priority += 2
        # pattern = u"中标.{1,30}$"  # 公司字符串前最多间隔15个字符有前缀 "中标单位|供应商|中标人|供货商"
        # if re.search(pattern, texts[i][0]) is not None:
        #     priority += 1
        # pattern = u"[^，；。？!]{0,10}(?:中标单位|供应商|中标人|供货商|中标候选人|成交单位)"  # 公司字符串前最多间隔15个字符有前缀 "中标单位|供应商|中标人|供货商"
        # if re.match(pattern, texts[i][1]) is not None:
        #     priority += 4

        # 确定不是中标单位的反向信息
        pattern = u"(?:代理|招标|采购|采购|发布)(?:机构|单位|人).{0,10}$"  # 公司字符串前最多间隔15个字符有前缀 "中标单位|供应商|中标人|供货商"
        if re.search(pattern, texts[i][0]) is not None:
            priority -= 16
        pattern = u"(?:代理|采购).{0,20}$"  # 公司字符串前最多间隔15个字符有前缀 "中标单位|供应商|中标人|供货商"
        if re.search(pattern, texts[i][0]) is not None:
            priority -= 4
        pattern = u"委托[^，；。？!]{0,50}$"  # 公司字符串前最多间隔15个字符有前缀 "中标单位|供应商|中标人|供货商"
        if re.search(pattern, texts[i][0]) is not None:
            priority -= 4
        pattern = u"[^，；。？!]{0,50}委托"  # 公司字符串前最多间隔15个字符有前缀 "中标单位|供应商|中标人|供货商"
        if re.match(pattern, texts[i][1]) is not None:
            priority -= 4
        # 公司名称不能用“招标”，排除招标公司
        pattern = u"招标|招(投)标|代理|咨询"
        if re.search(pattern, company_strings[i]) is not None:
            priority -= 16

        # 如果是在中标信息段落下的情况
        pattern = u"(?:中标|成交)(?:信息|情况)>>"
        if re.search(pattern, text) is not None:
            priority *= 2

        company_info = {"priority": priority, "inline_pos": i, "company": company_strings[i], "level": level}
        result.append(company_info)
    return result


def find_valid_money(text):
    number = u"零壹贰叁肆伍陆柒捌玖拾"
    money_pattern = u"[壹贰叁肆伍陆柒捌玖拾]+[%s佰仟百千万亿]*[元圆]+(?:整|[%s]+角[%s]+分|[%s]+角|[%s]+分)" % (
        number, number, number, number, number)  # 先选择繁体数字
    re_money = re.compile(money_pattern)
    money_strings = re_money.findall(text)
    if len(money_strings) <= 0:  # 再选择阿拉伯数字
        money_pattern = u"\d+[\d,，]*(?:\.?\d*)"
        re_money = re.compile(money_pattern)
        money_strings = re_money.findall(text)
    return money_strings


def get_bid_money(text):
    """
    获取金额信息
    :param text:
    :return:
    """
    money_strings = find_valid_money(text)
    contexts = split_text_by_strings(money_strings, text)

    result = []
    for i in range(len(money_strings)):
        priority = 0
        pref, suff = contexts[i][0][-20:], contexts[i][1][:20]

        money_unit_pattern = u"(?:百|千|万|百万|千万|亿)[美]?元[/∕/]{1}[\u4e00-\u9fa5]+|" + \
                             u"[美]?元[/∕/]{1}[\u4e00-\u9fa5]+|" + \
                             u"(?:百|千|万|百万|千万|亿)[美]?元|" + \
                             u"[美]?元"
        re_money_unit = re.compile(money_unit_pattern)
        money_unit_strings = re_money_unit.findall("\t".join((pref, suff)))
        if len(money_unit_strings) > 0:
            unit = money_unit_strings[0]
            unit = unit.replace(u"∕", u"/")
            items = unit.split(u"/")
            if len(items) == 2 and items[-1] in [u"人民币", u"美元"]:
                unit = items[0]
        else:
            unit = None

        currency_pattern_cn = u"人民币|RMB|￥"
        currency_pattern_us = u"美元|USD|\$"
        if re.search(currency_pattern_cn, "\t".join((pref, suff))) is not None:
            currency = u"人民币"
        elif re.search(currency_pattern_us, "\t".join((pref, suff))) is not None:
            currency = u"美元"
        else:
            currency = None

        money_pattern_0 = u"(?:中标|成交|中标（成交）|成交（中标）|投标|竞标)(?:|单位|供应商|供货商|商|人)(?:金额|报价|总价|价格|价).{0,30}$"
        money_pattern_1 = u"(?:金额|报价|总价|价格|价).{0,10}$"
        if re.search(money_pattern_0, contexts[i][0]) is not None:  # 金额字符串前最多间隔15个字符有前缀 "中标|报价"
            priority += 4
        elif re.search(money_pattern_1, contexts[i][0]) is not None:
            priority += 2

        if len(money_unit_strings) > 0 or currency is not None:   # 表明是金额
            priority += 1

        if money_strings[i][0] in u"壹贰叁肆伍陆柒捌玖拾":  # 如果是大写金额
            priority += 16
            unit = u"元"
            currency = u"人民币"
        else:
            if len(contexts[i][1]) > 0 and contexts[i][1][0] not in u"  ()（）十百千万亿美元":  # 如果数字后面不是跟的"元"或空
                priority -= 32

        # 如果是在中标信息段落下的情况
        pattern = u"(?:中标|成交)(?:信息|情况)>>"
        if re.search(pattern, text) is not None:
            priority *= 2

        money_info = {"priority": priority, "inline_pos": i, "money": money_strings[i], "unit": unit,
                      "currency": currency}
        result.append(money_info)

    return result


def find_all_possible_info(document):
    """
    找到所以可能的字段
    :param document:
    :return:
    """
    lists = document

    bid_time = []
    bid_company = []
    bid_money = []
    for i in range(len(lists)):
        line_num = {"line_num": i}
        # 获取中标时间
        r = get_bid_time(lists[i])
        if len(r) > 0:
            [x.update(line_num) for x in r]
            bid_time += r
        # 获取单位名称
        r = get_bid_company(lists[i])
        if len(r) > 0:
            [x.update(line_num) for x in r]
            bid_company += r
        # 获取中标金额
        r = get_bid_money(lists[i])
        if len(r) > 0:
            [x.update(line_num) for x in r]
            bid_money += r

    # 取最有可能的时间作为中标时间
    if len(bid_time) > 0:
        bid_time = sorted(bid_time, key=lambda x: x["priority"], reverse=True)  # 按优先级排序
        if bid_time[0]["priority"] > 0:
            bid_time = bid_time[0]["time"]
        else:
            bid_time = ""
    else:
        bid_time = ""

    # 取最有可能的公司名作为中标公司
    if len(bid_company) > 0:
        bid_company = sorted(bid_company, key=lambda x: x["priority"], reverse=True)  # 按优先级排序
        tmp = [x["company"] for x in bid_company if x["priority"] < 0]  # 取出所以已经被标记为不是中标单位的单位
        max_priority = max(bid_company[0]["priority"], 4)
        bid_company = [x for x in bid_company if x["priority"] == max_priority and x["company"] not in tmp]

    # 取最有可能的金额作为中标金额
    if len(bid_money) > 0:
        bid_money = sorted(bid_money, key=lambda x: x["priority"], reverse=True)  # 按优先级排序
        max_priority = max(bid_money[0]["priority"], 1)
        bid_money = [x for x in bid_money if x["priority"] == max_priority]

    return bid_time, bid_company, bid_money


def match(distance_matrix):
    """
    # 使用动态规划，搜索所以可能情况
    :param distance_matrix:
    :return:
    """
    is_transposed = False
    row_num, col_num = distance_matrix.shape
    if row_num > col_num:
        distance_matrix = distance_matrix.T
        row_num, col_num = col_num, row_num
        is_transposed = True

    cost_0 = np.ones_like(distance_matrix)  # 正向的损失值
    route_0 = np.zeros_like(distance_matrix, dtype=int)  # 正向的路径
    cost_1 = np.ones_like(distance_matrix)  # 反向的损失值
    route_1 = np.zeros_like(distance_matrix, dtype=int)  # 反向的路径

    space = col_num - row_num + 1  # 可以调整的空间

    for j in range(space):  # 初始化第一行的损失值
        if distance_matrix[0][j] > 0:
            c0 = abs(distance_matrix[0][j])
            c1 = abs(distance_matrix[0][j]) * 10
        else:
            c0 = abs(distance_matrix[0][j]) * 10
            c1 = abs(distance_matrix[0][j])
        cost_0[0][j] = c0
        cost_1[0][j] = c1

    for i in range(1, row_num):
        for j in range(i, i + space):
            if distance_matrix[i][j] > 0:
                c0 = abs(distance_matrix[i][j])
                c1 = abs(distance_matrix[i][j]) * 10
            else:
                c0 = abs(distance_matrix[i][j]) * 10
                c1 = abs(distance_matrix[i][j])
            t0, t1 = None, None
            for k in range(i - 1, j):
                if t0 is None or cost_0[i - 1][k] + c0 < t0:
                    t0 = cost_0[i - 1][k] + c0
                    route_0[i][j] = k
                if t1 is None or cost_1[i - 1][k] + c1 < t1:
                    t1 = cost_1[i - 1][k] + c1
                    route_1[i][j] = k
            cost_0[i][j] = t0
            cost_1[i][j] = t1

    t, route, dirct = None, None, None
    for k in range(row_num - 1, col_num):
        if t is None or cost_0[-1][k] < t:
            t = cost_0[-1][k]
            route, dirct = k, 0
        if t is None or cost_1[-1][k] < t:
            t = cost_1[-1][k]
            route, dirct = k, 1

    match_i = [route]
    for i in range(row_num - 1, 0, -1):
        if dirct == 0:
            match_i.append(route_0[i][match_i[-1]])
        else:
            match_i.append(route_1[i][match_i[-1]])
    match_i.reverse()

    origin_i = list(range(row_num))
    if is_transposed:
        origin_i, match_i = match_i, origin_i

    return dict(zip(origin_i, match_i))


def assemble_company_money(bid_company, bid_money):
    """
    按公司名称将公司、中标金额、金额单位进行组合
    :param bid_company:
    :param bid_money:
    :return:
    """
    # 公司名称、中标金额、金额单位按出现顺序排序
    bid_company = sorted(bid_company, key=lambda x: x["inline_pos"])
    bid_company = sorted(bid_company, key=lambda x: x["line_num"])
    bid_money = sorted(bid_money, key=lambda x: x["inline_pos"])
    bid_money = sorted(bid_money, key=lambda x: x["line_num"])

    com_mon = []
    company_num, money_num = len(bid_company), len(bid_money)
    if money_num == 0:  # 如果中标金额为未知，记为0
        com_mon = []
        for com in bid_company:
            t = {"winning_company": com["company"],
                 "winning_amount": None,
                 "unit": None,
                 "currency": None}
            com_mon.append(t)
    elif company_num > 0:  # 中标公司数量少于中标金额
        dis_matrix = np.ones((company_num, money_num))  # 中标公司与金额之间的距离
        for i in range(company_num):
            for j in range(money_num):
                dis_matrix[i][j] = (bid_money[j]["line_num"] - bid_company[i]["line_num"]) + \
                                   (bid_money[j]["inline_pos"] - bid_company[i]["inline_pos"]) * 0.001

        # 根据距离找到最佳匹配
        match_i = match(dis_matrix)

        com_mon = []
        for i in range(company_num):
            if i not in match_i:
                t = {"winning_company": bid_company[i]["company"],
                     "winning_amount": None,
                     "unit": None,
                     "currency": None}
                com_mon.append(t)
                continue
            else:
                matched_money = bid_money[match_i[i]]
                t = {"winning_company": bid_company[i]["company"],
                     "winning_amount": matched_money["money"],
                     "unit": matched_money["unit"],
                     "currency": matched_money["currency"]}
                com_mon.append(t)

    # 去掉重复的中标公司项，包括可能重复的
    uniq_com_mon = []
    com_mon = sorted(com_mon, key=lambda x: x["winning_amount"], reverse=True)
    com_mon = sorted(com_mon, key=lambda x: x["winning_company"], reverse=True)
    for com in com_mon:
        mark = False
        for ucom in uniq_com_mon:
            if com["winning_company"] == ucom["winning_company"] and (
                            com["winning_amount"] == ucom["winning_amount"] or com["winning_amount"] is None):
                mark = True
                break
        if mark is False:
            uniq_com_mon.append(com)

    return uniq_com_mon


def find_all_info(document):
    """
    从已经分解了的html文档中找到：中标时间、中标公司、中标金额(单位)
    :param document:
    :return:
    """
    bid_time, bid_company, bid_money = find_all_possible_info(document)
    # 规范化中标时间格式
    bid_time = regular_time(bid_time)
    # 规范化中标金额
    bid_money = [regular_money(mon) for mon in bid_money]
    # 将公司名称，中标金额及单位进行组合
    com_mon = assemble_company_money(bid_company, bid_money)

    result = {"bid_time": bid_time, "bid_result": com_mon}
    return result
