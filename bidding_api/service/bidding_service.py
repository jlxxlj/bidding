# coding=utf-8
# author="Jianghua Zhao"
import json
import os
import re
import bs4
import sys
from collections import OrderedDict

import base64

import requests
import boto3

from dao import sc_crawler_query_all, sc_crawler_query_one
from dao import sc_crawler_non_query
from bidding_service_sql import *

reload(sys)
sys.setdefaultencoding('utf-8')

CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))

nations = [u"汉族", u"蒙古族", u"回族", u"藏族", u"维吾尔族", u"苗族", u"彝族", u"壮族", u"布依族", u"朝鲜族", u"满族", u"侗族",
           u"瑶族", u"白族", u"土家族", u"哈尼族", u"哈萨克族", u"傣族", u"黎族", u"僳僳族", u"佤族", u"畲族", u"高山族",
           u"拉祜族", u"水族", u"东乡族", u"纳西族", u"景颇族", u"柯尔克孜族", u"土族", u"达斡尔族", u"仫佬族", u"羌族",
           u"布朗族", u"撒拉族", u"毛南族", u"仡佬族", u"锡伯族", u"阿昌族", u"普米族", u"塔吉克族", u"怒族", u"乌孜别克族",
           u"俄罗斯族", u"鄂温克族", u"德昂族", u"保安族", u"裕固族", u"京族", u"塔塔尔族", u"独龙族", u"鄂伦春族", u"赫哲族",
           u"门巴族", u"珞巴族", u"基诺族", u"傈僳族", u"维吾尔", u"哈萨克", u"柯尔克孜", u"达斡尔", u"塔吉克", u"乌孜别克",
           u"俄罗斯", u"鄂温克", u"塔塔尔", u"鄂伦春"]

re_nations = re.compile(u"|".join(nations))
re_suffix_new = re.compile(u"(?:自治)?(?:省|区|市|州|地区|盟|县|新?区|旗|群岛的岛礁及其海域|群岛)$")
re_suffix = re.compile(u"(?:自治)?(?:省|区|市|州|地区|盟|县|区|旗|群岛的岛礁及其海域|群岛)$")


def get_keyword(address):
    if isinstance(address, str):
        address = unicode(address)
    address_keyword = re_suffix_new.sub(u"", address)
    if len(address_keyword) < 2:
        address_keyword = re_suffix.sub(u"", address)
    address_keyword = re_nations.sub(u"", address_keyword)
    if len(address_keyword) < 2:
        address_keyword = address
    return address_keyword


with open(os.path.join(CURRENT_FOLDER, "region_code_index.json")) as f:
    REGION_CODE_INDEX = json.load(f)
    CODE_TO_REGION = REGION_CODE_INDEX["codeToRegion"]
    REGION_TO_CODE = REGION_CODE_INDEX["regionToCode"]


def get_region(pvc, cty):
    province, city, county = None, None, None

    if re.search(u"^\d+$", pvc):
        pvc_code = pvc
        if pvc_code in CODE_TO_REGION and len(CODE_TO_REGION[pvc_code]) == 1:
            pvc_short_name = get_keyword(CODE_TO_REGION[pvc][0])
        else:
            return province, city, county
    else:
        pvc_short_name = get_keyword(pvc)
        if pvc_short_name in REGION_TO_CODE:
            pvc_code = get_keyword(REGION_TO_CODE[pvc_short_name])
        else:
            return province, city, county

    if re.search(u"^[\u4E00-\u9FA5]+$", cty):
        cty_short_name = pvc_short_name + get_keyword(cty)
        if cty_short_name in REGION_TO_CODE:
            cty_code = REGION_TO_CODE[cty_short_name]
        else:
            return province, city, county
    else:
        cty_code = pvc_code + cty

    region_code = cty_code if cty_code else pvc_code
    if region_code in CODE_TO_REGION:
        region = CODE_TO_REGION[region_code]
        province = region[0]
        if len(region) > 1:
            if province in (u"北京市", u"上海市", u"天津市", u"重庆市"):
                county = region[1]
            else:
                city = region[1]

    return province, city, county


def transform_amount(dict_list):
    for i, item in enumerate(dict_list):
        if "amount" in item:
            dict_list[i]["amount"] = round(item["amount"] / 10000, 2)
        if "unit" in item and item.get("unit"):
            dict_list[i]["unit"] = u"万" + item.get("unit")
    return dict_list


def get_statistic_query(query_str, project_type, province, city, county):
    constrain = "AND announce.project_type=%(project_type)s " if project_type else ""
    constrain += "AND announce.province=%(province)s " if province else ""
    constrain += "AND announce.city=%(city)s " if city else ""
    constrain += "AND announce.county=%(county)s " if county else ""
    return query_str.format(user_constrain=constrain)


def bidding_statistic_service(op, begin, end, project_type=None, province=None, city=None, county=None, top=10, page=0,
                              page_size=10):
    parameters = {"start_date": begin, "end_date": end, "project_type": project_type, "skip_n": page * page_size,
                  "province": province, "city": city, "county": county, "page_size": page_size, "top_n": top}

    sc_crawler_non_query(set_work_mem_32m_non_query)

    if op == "amountCountRegion":
        if not province:
            query = get_statistic_query(nation_amount_count_base_on_province_query, project_type, province, city=None,
                                        county=None)
            result = sc_crawler_query_all(query, parameters)
        elif province in (u"北京市", u"上海市", u"天津市", u"重庆市"):
            query = get_statistic_query(province_amount_count_base_on_county_query, project_type, province, city=None,
                                        county=None)
            result = sc_crawler_query_all(query, parameters)
            region, default_region_name = u"county", u"市级"
            t = [i for i in range(len(result)) if result[i][region] is None]
            for i in t:
                result[i][region] = default_region_name
            for i, it in enumerate(result):
                result[i]["city"] = it["county"]
                del result[i]["county"]
        else:
            query = get_statistic_query(province_amount_count_base_on_city_query, project_type, province, city=None,
                                        county=None)
            result = sc_crawler_query_all(query, parameters)
            region, default_region_name = u"city", u"省级"
            t = [i for i in range(len(result)) if result[i][region] is None]
            for i in t:
                result[i][region] = default_region_name

        for i, it in enumerate(result):
            for reg in ["province", "city", "county"]:
                if reg in it:
                    result[i]["shortName"] = get_keyword(it[reg])
                    break

        return transform_amount(result)

    elif op == "amountCountDate":
        query = get_statistic_query(amount_count_base_on_date_query, project_type, province, city, county)
        result = sc_crawler_query_all(query, parameters)
        return transform_amount(result)

    elif op == "topRole":
        query = get_statistic_query(top_n_amount_base_on_purchaser_query, project_type, province, city, county)
        top_pur = transform_amount(sc_crawler_query_all(query, parameters))
        query = get_statistic_query(top_n_amount_base_on_agent_query, project_type, province, city, county)
        top_agt = transform_amount(sc_crawler_query_all(query, parameters))
        query = get_statistic_query(top_n_amount_base_on_winner_query, project_type, province, city, county)
        top_win = transform_amount(sc_crawler_query_all(query, parameters))
        if len(top_pur) > 0 or len(top_agt) or len(top_win) > 0:
            result = {"topPurchasers": top_pur, "topAgents": top_agt, "topWinners": top_win}
        else:
            result = None
        return result

    elif op == "winnerInfo":
        query = get_statistic_query(winner_info_query, project_type, province, city, county)
        result = sc_crawler_query_all(query, parameters)
        for i, item in enumerate(result):
            if province in (u"北京市", u"上海市", u"天津市", u"重庆市"):
                result[i]["city"] = item["county"]
            del result[i]["county"]
        return transform_amount(result)

    elif op == "winnerInfoCount":
        query = get_statistic_query(winner_info_count_query, project_type, province, city, county)
        result = sc_crawler_query_one(query, parameters)
        return result

    else:
        return []


# 公司中标信息查询服务
AWS_ACCESS_KEY_ID = "AKIAPQSZXOZS5YSMKLIQ"
AWS_SECRET_ACCESS_KEY = "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"
AWS_REGION_NAME = "cn-north-1"

aws_session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                            region_name=AWS_REGION_NAME)
s3 = aws_session.resource(service_name="s3")


def coding_filter(data_list):
    for it in data_list:
        for k, v in it.items():
            if isinstance(v, str):
                it[k] = v.decode("utf-8")


def collect_participator(parts):
    # 排序
    parts = sorted(parts, key=lambda xx: xx["resultID"])
    segments = OrderedDict()
    for pt in parts:
        if pt["segmentName"] not in segments:
            segments[pt["segmentName"]] = []
        flag, idx = False, 0
        for i, it in enumerate(segments[pt["segmentName"]]):
            if it[0] == pt["winningCompany"]:
                flag, idx = True, i
                break
        if flag:
            segments[pt["segmentName"]][idx][1].append(pt["roleName"])
            if not segments[pt["segmentName"]][idx][2] and pt["winningAmount"]:
                segments[pt["segmentName"]][idx][2] = pt["winningAmount"]
            if not segments[pt["segmentName"]][idx][3] and pt["unit"]:
                segments[pt["segmentName"]][idx][3] = pt["unit"]
        else:
            segments[pt["segmentName"]].append(
                [pt["winningCompany"], [pt["roleName"]], pt["winningAmount"], pt["unit"]])
    participator = []
    for k, v in segments.items():
        for idx, it in enumerate(v):
            it = {"winningCompany": it[0], "roleName": it[1], "winningAmount": it[2], "unit": it[3]}
            v[idx] = it
        participator += v
    return participator


def participator_to_string(participators):
    result_str = u""
    for pt in participators:
        result_str += pt.get("winningCompany", "")
        t = unicode(pt.get("winningAmount", "")) if pt.get("winningAmount") else ""
        t += unicode(pt.get("unit", "")) if t and pt.get("unit") else ""
        mon = [t] if t else []
        t = u",".join([x for x in (pt.get("roleName", []) + mon) if x])
        result_str += u"(%s);" % t if t else u";"
    return result_str


def build_beautifulsoup(html):
    return bs4.BeautifulSoup(html, "html.parser")


def purify_navistring_attr(tag):
    for child in tag.children:
        if isinstance(child, bs4.Comment):  # 删除标签文档中的注释
            child.extract()
        elif isinstance(child, bs4.NavigableString):  # 删除标签文本前后的空白字符
            child.replace_with(child.strip().replace(u"？", u" "))
        elif isinstance(child, bs4.Tag):
            if child.name in ("td", "th"):  # 保留表格中的 "colspan" 和 "rowspan"属性
                t = {}
                if "colspan" in child.attrs:
                    t["colspan"] = child["colspan"]
                if "rowspan" in child.attrs:
                    t["rowspan"] = child["rowspan"]
                child.attrs = t
            else:
                child.attrs = None  # 删除标签中的属性
            purify_navistring_attr(child)


def purify_html(html):
    html = unicode(html)
    bs = build_beautifulsoup(html)
    purify_navistring_attr(bs)
    return str(bs)


def get_content_source_key(content_source):
    if isinstance(content_source, basestring):
        content_source = content_source.replace("s3:bidding:", "", 1)
        return base64.b64encode(content_source)
    return None


def get_content_source_by_key(source_key, with_b64decode=False):
    try:
        if with_b64decode:
            source_key = base64.b64decode(source_key)
        source_data = s3.Object("bidding", source_key).get()
        source_data = json.loads(source_data["Body"].read())
        r = source_data.get("content", "")
    except Exception as e:
        return None
    return purify_html(r) if r else ""


# 52.80.91.57 172.31.25.55
def get_company_history_names(company_name):
    res = requests.post(url='http://172.31.25.55:9030/company/profile/feature/batch',
                        data=json.dumps({'feaType': 'custom',
                                         'companyNameList': [company_name],
                                         'source': ['historyName']}))
    if res.status_code != 200:
        raise Exception(u"查询公司历史名称失败，请确认接口是否可访问。")
    names = res.json().get("result", [])
    if names:
        names = names[0].get("historyName", [])
        names = [it.get("name") for it in names]
    return list(set([company_name] + names))


def bidding_company_info_service(company_name, st_datetime, ed_datetime):
    items = sc_crawler_query_all(company_bidding_info_query, (company_name, st_datetime, ed_datetime))
    coding_filter(items)

    announce_id, participator, result, results = None, [], {}, []
    for item in items:
        if announce_id != item["announceID"]:
            announce_id = item["announceID"]
            if participator and result:
                result["participatorObject"] = collect_participator(participator)
                result["participator"] = participator_to_string(result["participatorObject"])
                results.append(result)
                participator, result = [], {}

        if not result:
            result["announceID"] = item["announceID"]
            result["title"] = item["title"]
            result["url"] = item["url"]
            result["sourceKey"] = get_content_source_key(item["contentSource"])
            result["website"] = item["website"]
            result["publishedDateTime"] = item["publishedDateTime"]
            result["winningDate"] = item["winningDate"]
            result["announceType"] = item["announceType"]

        part = {
            "resultID": item["resultID"],
            "winningCompany": item["winningCompany"],
            "winningAmount": item["winningAmount"],
            "unit": item["unit"],
            "currency": item["currency"],
            "roleName": item["roleName"],
            "candidateRank": item["candidateRank"],
            "segmentName": item["segmentName"]
        }
        participator.append(part)

    if participator and result:
        result["participatorObject"] = collect_participator(participator)
        result["participator"] = participator_to_string(result["participatorObject"])
        # result["participator"] = participator_to_string(participator)
        results.append(result)

    return results


def merged_bidding_company_info_service(company_name, st_datetime, ed_datetime):
    history_names = get_company_history_names(company_name)

    results = []
    for name in history_names:
        results += bidding_company_info_service(name, st_datetime, ed_datetime)

    results = sorted(results, key=lambda x: x["publishedDateTime"], reverse=True)

    return results


def bidding_content_source_service(source_key, announce_id):
    if announce_id:
        res = sc_crawler_query_one(company_bidding_content_source_query, (announce_id,))
        if res and res.get("contentSource"):
            source_key = res.get("contentSource").replace("s3:bidding:", "", 1)
            return get_content_source_by_key(source_key)
    elif source_key:
        return get_content_source_by_key(source_key, with_b64decode=True)
    return None


def bidding_info_service(announce_id, url):
    participator = None
    if announce_id:
        participator = sc_crawler_query_all(company_bidding_info_by_id_query, (announce_id,))
    elif url:
        participator = sc_crawler_query_all(company_bidding_info_by_url_query, (url,))
    if participator:
        participator_object = collect_participator(participator)
        result = {
            "announceID": participator[0]["announceID"],
            "title": participator[0]["title"],
            "url": participator[0]["url"],
            "sourceKey": get_content_source_key(participator[0]["contentSource"]),
            "website": participator[0]["website"],
            "publishedDateTime": participator[0]["publishedDateTime"],
            "winningDate": participator[0]["winningDate"],
            "announceType": participator[0]["announceType"],
            "participatorObject": participator_object,
            "participator": participator_to_string(participator_object)
        }
        return result
    return None


# ************************************** #
# 对公司的投标中标情况进行统计分析
# ************************************** #

def _format_statistic_by_company_result_data(data):
    # 统一返回的数据格式：Amount字段为零且对应count大于0时设为None；
    for idx, item in enumerate(data):
        if item.get("bidCount") == 0:
            data[idx]["bidMoneyAmount"] = 0
        elif item.get("bidCount") > 0 and item.get("bidMoneyAmount") == 0:
            data[idx]["bidMoneyAmount"] = None
        elif item.get("bidMoneyAmount"):
            data[idx]["bidMoneyAmount"] = round(item.get("bidMoneyAmount"), 2)

        if item.get("winCount") == 0:
            data[idx]["winMoneyAmount"] = 0
        elif item.get("winCount") > 0 and item.get("winMoneyAmount") == 0:
            data[idx]["winMoneyAmount"] = None
        elif item.get("winMoneyAmount"):
            data[idx]["winMoneyAmount"] = round(item.get("winMoneyAmount"), 2)

    return data


def bidding_statistic_by_company_service(company_name, begin, end):
    parameters = {"company_name": company_name, "start_date": begin, "end_date": end}
    distribute = sc_crawler_query_all(bidding_result_statistic_by_company_query, parameters)
    statistic = {"bidCount": 0, "bidMoneyAmount": 0, "winCount": 0, "winMoneyAmount": 0}
    for item in distribute:
        for key in statistic.keys():
            statistic[key] += item[key] if item[key] else 0

    distribute.append(statistic)
    distribute = _format_statistic_by_company_result_data(distribute)
    distribute, statistic = distribute[:-1], distribute[-1]

    # 如果 statistic 中总投标次数为0时，返回None
    if statistic.get("bidCount") == 0:
        result = None
    else:
        result = {"provinceDistribution": distribute, "statistic": statistic}

    return result


# 合并多个统计结果
def _merge_statistic_result(obj_result, result):
    _number_type = (int, float, long)
    for k, v in result.items():
        if k not in obj_result:
            obj_result[k] = v
        else:
            if isinstance(v, dict):
                _merge_statistic_result(obj_result[k], v)
            elif isinstance(v, list):
                opvc = [_.get("province") for _ in obj_result[k]]
                resident = []
                for it in v:
                    pvc = it.get("province")
                    if pvc in opvc:
                        idx = opvc.index(pvc)
                        _merge_statistic_result(obj_result[k][idx], it)
                    else:
                        resident.append(it)
                obj_result[k] += resident
            else:
                if isinstance(obj_result[k], _number_type) and isinstance(v, _number_type):
                    obj_result[k] += v
                elif not isinstance(obj_result[k], _number_type) and isinstance(v, _number_type):
                    obj_result[k] = v


def merged_bidding_statistic_by_company_service(company_name, begin, end):
    history_names = get_company_history_names(company_name)

    results = {}
    for name in history_names:
        res = bidding_statistic_by_company_service(name, begin, end)
        if res:
            _merge_statistic_result(results, res)

    if not results:
        results = None

    return results


def bidding_statistic_by_company_trend_service(company_name, base):
    parameters = {"company_name": company_name}
    trend_data = sc_crawler_query_all(bidding_result_statistic_by_company_trend_query, parameters)

    trend = {}
    for item in trend_data:
        year_month = item.pop("yearMonth")
        month = int(year_month[-2:])
        month = int((month - 1) / base) * base + 1
        year_month = year_month[:-2] + "%02d" % month
        if year_month not in trend:
            trend[year_month] = []
        trend[year_month].append(item)

    result = {}
    for year_month, distribute in trend.items():
        statistic = {"bidCount": 0, "bidMoneyAmount": 0, "winCount": 0, "winMoneyAmount": 0}

        distribute_collect = {}
        for item in distribute:
            province = item.get("province")
            if province not in distribute_collect:
                distribute_collect[province] = item
                for key in statistic.keys():
                    distribute_collect[province][key] = item[key] if item[key] else 0
            else:
                for key in statistic.keys():
                    distribute_collect[province][key] += item[key] if item[key] else 0
        distribute = distribute_collect.values()

        for item in distribute:
            for key in statistic.keys():
                statistic[key] += item[key] if item[key] else 0

        distribute.append(statistic)
        distribute = _format_statistic_by_company_result_data(distribute)
        distribute, statistic = distribute[:-1], distribute[-1]

        result[year_month] = {"provinceDistribution": distribute, "statistic": statistic}

    return result


def merged_bidding_statistic_by_company_trend_service(company_name, base):
    history_names = get_company_history_names(company_name)

    results = {}
    for name in history_names:
        res = bidding_statistic_by_company_trend_service(name, base)
        if res:
            _merge_statistic_result(results, res)

    if not results:
        results = None

    return results
