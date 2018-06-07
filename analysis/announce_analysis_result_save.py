# coding=utf-8
# author="Jianghua Zhao"
"""
对招投标公告文档进行解析，提取其中有用信息
"""
import copy
import hashlib
import sys
import re
import json
from psycopg2.extras import RealDictCursor

from scpy.logger import get_logger

from scpy.date_extractor import extract_first_date

from toolkit.location_complement import search_full_region, get_region_max_level

from announce_attributes import *
from announce_analysis_result_key_map import announce_keys_map, result_keys_map

from config import config

reload(sys)
sys.setdefaultencoding('utf-8')

logger = get_logger(__file__)

RESOURCE = {}


def get_database():
    if not RESOURCE.get("database"):
        from db.postgresql_sc import PostgresqlUtil
        RESOURCE["database"] = PostgresqlUtil()
    return RESOURCE.get("database")


def get_save_service_session():
    if not RESOURCE.get("save_service_session"):
        import requests
        RESOURCE["save_service_session"] = requests.session()
    return RESOURCE.get("save_service_session")


def key_filter(data, key_set):
    assert isinstance(data, dict)
    for key in data.keys():
        if key not in key_set:
            del data[key]
        elif not key.endswith("_ts") and isinstance(data.get(key), unicode):
            data[key] = re.sub(u"[\s ]+", u"", data[key])


def complete_region(announce_data):
    # 从公告标题等字段提取位置信息
    cad_region_fields = ["region", "project_name", "title", "purchaser"]

    full_region = None
    full_level = 0
    for field in cad_region_fields:
        region = search_full_region(announce_data.get(field, ""))
        level = get_region_max_level(region)
        if level > full_level:
            full_level = level
            full_region = region

    if full_region:
        if full_region.get("province"):
            announce_data["province"] = full_region.get("province")
        if full_region.get("city"):
            announce_data["city"] = full_region.get("city")
        if full_region.get("county"):
            announce_data["county"] = full_region.get("county")


# 计算公告 unique-code
def get_announce_unique_code(announce):
    province = announce.get("province")
    purchaser = announce.get("purchaser")
    purchase_agent = announce.get("purchase_agent")
    # project_name = announce.get("project_name")
    project_id = announce.get("project_id")

    bidding_result = announce["result"]

    # 排好序
    keys = ["winning_company", "winning_amount", "unit", "currency", "role_type", "role_name",
            "candidate_rank", "segment_name", "company_address"]
    for key in keys[::-1]:
        bidding_result = sorted(bidding_result, key=lambda x: x.get(key))

    announce_str = ""
    announce_str += province if province else ""
    announce_str += purchaser if purchaser else ""
    announce_str += purchase_agent if purchase_agent else ""
    # announce_str += project_name if project_name else ""
    announce_str += project_id if project_id else ""
    for item in bidding_result:
        announce_str += str(item.get("winning_company"))
        announce_str += str(item.get("winning_amount"))
        announce_str += str(item.get("unit"))
        announce_str += str(item.get("currency"))
        # announce_str += str(item.get("role_type")
        # announce_str += str(item.get("role_name")
        # announce_str += str(item.get("candidate_rank")
        # announce_str += str(item.get("segment_name")
        # announce_str += str(item.get("company_address")
    announce_str = re.sub("（", "(", announce_str)
    announce_str = re.sub("）", ")", announce_str)
    announce_str = re.sub("【", "[", announce_str)
    announce_str = re.sub("】", "]", announce_str)
    # 计算hash值
    sh = hashlib.sha256()
    sh.update(announce_str)
    unique_code = sh.hexdigest()

    return unique_code


def fix_datetime(date_tm):
    if isinstance(date_tm, basestring):
        date_tm = extract_first_date(date_tm, is_str=False)
    if date_tm.hour == 0 and date_tm.minute == 0 and date_tm.second == 0:
        date_tm += datetime.timedelta(hours=23, minutes=59, seconds=59)
    return date_tm


def check_announce_repeat(announce_data, participator):
    database = get_database()

    # 计算公告的唯一标示码
    tmp_announce = copy.deepcopy(announce_data)
    tmp_announce["result"] = participator
    unique_code = get_announce_unique_code(tmp_announce)
    url = announce_data["url"]

    sql = "SELECT * FROM bidding_announce WHERE unique_code=%s AND url<>%s AND status<98"
    sql_2 = "UPDATE bidding_announce SET status=98 WHERE id=%s"

    conn = database.get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(sql, (unique_code, url))
    saved_announce = cur.fetchone()

    status = 0
    if saved_announce:
        dt = fix_datetime(announce_data["published_ts"])
        sdt = fix_datetime(saved_announce["published_ts"])
        if dt < sdt < dt + datetime.timedelta(days=365):
            cur.execute(sql_2, (saved_announce["id"],))
            cur.close()
            conn.commit()
        elif sdt <= dt < sdt + datetime.timedelta(days=365):
            status = 98
    database.put_conn(conn)

    announce_data["unique_code"] = unique_code
    announce_data["status"] = status


def save_bidding_result(announce_data, source):
    """
    保存中标结果
    :param announce_data:
    :param source:
    :return:
    """
    database = get_database()

    # announce_data = json.loads(announce_data)
    announce_data = copy.deepcopy(announce_data)
    if not announce_data.get("url"):
        return
    announce_data["content_source"] = source

    complete_region(announce_data)

    participator = announce_data.pop("participator", [])
    if participator is None or len(participator) == 0:
        # 删除数据库中记录
        update_condition = {"url": announce_data.get("url")}
        bidding_announce = database.select(table="bidding_announce", condition=update_condition)
        if len(bidding_announce) > 0:
            # bidding_announce_id = bidding_announce[0][0]
            # delete_condition = {"bidding_announce_id": bidding_announce_id}
            # database.delete(table="bidding_result", condition=delete_condition)
            # database.delete(table="bidding_announce", condition=update_condition)
            announce_data["status"] = 3  # 解析结果不一致：新的解析结果中没有中标信息而以前有
            database.update(table="bidding_announce", condition=update_condition, data=announce_data)
        logger.info("There is no participator (%s)." % announce_data.get("url"))
        return

    key_filter(announce_data, announce_keys_map.keys())
    update_condition = {"url": announce_data.get("url")}

    bidding_announce = database.select(table="bidding_announce", condition=update_condition)
    if len(bidding_announce) > 0 and bidding_announce[0][-1] == 1:
        logger.info("This announce has been correctly analysed.")
        return

    check_announce_repeat(announce_data, participator)
    database.update(table="bidding_announce", condition=update_condition, data=announce_data,
                    upsert=True)

    bidding_announce = database.select(table="bidding_announce", condition=update_condition)
    bidding_announce_id = bidding_announce[0][0]
    delete_condition = {"bidding_announce_id": bidding_announce_id}
    database.delete(table="bidding_result", condition=delete_condition)

    for i, part in enumerate(participator):
        key_filter(part, result_keys_map.keys())
        part["bidding_announce_id"] = bidding_announce_id
        database.insert("bidding_result", part)

    logger.info("Write an analysis result (%s)." % announce_data.get("url"))


def announce_analysis_result_save(announce_data, source):
    from requests.exceptions import RequestException

    if config.USE_RESULT_SAVE_SERVICE:
        session = get_save_service_session()
        max_try = 60
        while max_try > 0:
            try:
                session.post(url=config.RESULT_SAVE_SERVICE_URL,
                             data=json.dumps({"announceData": announce_data, "source": source}),
                             headers={'Content-Type': 'application/json;charset=utf8'},
                             timeout=60)
                break
            except RequestException as e:
                time.sleep(10)
                logger.exception(e)
                max_try -= 1
                if max_try <= 0:
                    raise e
    else:
        save_bidding_result(announce_data, source)


if __name__ == "__main__":
    announce_analysis_result_save({}, "")
