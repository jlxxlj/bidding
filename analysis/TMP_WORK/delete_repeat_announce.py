# coding=utf-8
# author="Jianghua Zhao"

"""
处理重复的公告
"""
import copy
import hashlib

import psycopg2
from psycopg2.extras import RealDictCursor
from scpy.logger import get_logger

import sys
import os
import re

par_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if par_dir not in sys.path:
    sys.path.append(par_dir)

from announce_attributes import *

# from analysis import get_announce_unique_code

logger = get_logger(__file__)


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


def compute_announce_unique_code():
    # 查询数据库
    conn = psycopg2.connect(database="crawler", user="crawler", password="1qaz2wsx",
                            host="sc-db.cfdjbes8ghlt.rds.cn-north-1.amazonaws.com.cn", port="5432")

    def search_item():
        sql = """
            SELECT announce.id, announce.province, announce.purchaser, announce.purchase_agent, announce.project_name,
                   announce.project_id, result.winning_company, result.winning_amount, result.unit,
                   result.currency, result.role_type, result.role_name, result.candidate_rank,
                   result.segment_name, result.company_address
            FROM bidding_announce announce, bidding_result result
            WHERE announce.id=result.bidding_announce_id
            ORDER BY announce.id
        """
        # AND announce.unique_code IS NULL

        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql)
        id_, item_ = None, {}
        for it in cur:
            if id_ != it["id"]:
                id_ = it["id"]
                if item_:
                    yield item_
                item_ = copy.deepcopy(it)
                item_["result"] = []
            item_["result"].append(it)
        if item_.get("result"):
            yield item_
        cur.close()

    def update_one(item_):
        unique_code = get_announce_unique_code(item_)

        sql = """
            UPDATE bidding_announce
            SET unique_code=%s
            WHERE id=%s
        """

        cur = conn.cursor()
        cur.execute(sql, (unique_code, item_["id"]))
        cur.close()

    cnt = 0
    item = None
    for item in search_item():
        cnt += 1
        update_one(item)
        if cnt % 100 == 0:
            conn.commit()
            logger.info("update %s items id=%s" % (cnt, item["id"]))
    if cnt % 100 != 0:
        conn.commit()
        logger.info("update %s items id=%s" % (cnt, item["id"]))
    logger.info("update items done.")


def compute_announce_unique_code_by_pager():
    # 查询数据库
    conn = psycopg2.connect(database="crawler", user="crawler", password="1qaz2wsx",
                            host="sc-db.cfdjbes8ghlt.rds.cn-north-1.amazonaws.com.cn", port="5432")

    def search_item(start_id, page_size, order="asc"):
        sql = """
            SELECT announce.id, announce.province, announce.purchaser, announce.purchase_agent, announce.project_name,
                   announce.project_id, result.winning_company, result.winning_amount, result.unit,
                   result.currency, result.role_type, result.role_name, result.candidate_rank,
                   result.segment_name, result.company_address
            from bidding_announce announce, bidding_result result
            WHERE announce.id=result.bidding_announce_id
            AND announce.id>{0}
            ORDER BY announce.id {2}
            limit {1}
        """.format(start_id, page_size, order)
        # AND announce.unique_code IS NULL

        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql)
        id_, item_ = None, {}
        for it in cur:
            if id_ != it["id"]:
                id_ = it["id"]
                if item_:
                    yield item_
                item_ = copy.deepcopy(it)
                item_["result"] = []
            item_["result"].append(it)
        # if item_.get("result"):
        #     yield item_
        cur.close()

    def update_one(item_):
        unique_code = get_announce_unique_code(item_)

        sql = """
            UPDATE bidding_announce
            SET unique_code=%s
            WHERE id=%s
        """

        cur = conn.cursor()
        cur.execute(sql, (unique_code, item_["id"]))
        cur.close()

    cnt = 0
    item = None
    p_size = 10000
    pre_cnt = -1
    while cnt != pre_cnt:
        pre_cnt = cnt
        st_id = item["id"] if item else -1
        for item in search_item(st_id, p_size):
            cnt += 1
            update_one(item)
            if cnt % 100 == 0:
                conn.commit()
                logger.info("update %s items id=%s" % (cnt, item["id"]))
        if cnt % 100 != 0:
            conn.commit()
            logger.info("update %s items id=%s" % (cnt, item["id"]))

    logger.info("fix last item")
    for item in search_item(start_id=-1, page_size=1000, order="desc"):
        update_one(item)
        conn.commit()
        break

    logger.info("update items done.")


def delete_repeat_announce():
    # 查询数据库
    conn = psycopg2.connect(database="crawler", user="crawler", password="1qaz2wsx",
                            host="sc-db.cfdjbes8ghlt.rds.cn-north-1.amazonaws.com.cn", port="5432")

    def search_item():
        sql = """
                SELECT unique_code, count(*) AS "count"
                FROM bidding_announce
                WHERE status<98
                AND unique_code IS NOT NULL
                GROUP BY unique_code
                HAVING count(*) >1;
            """

        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql)
        for item_ in cur:
            yield item_

        cur.close()

    def update_one(item_):
        unique_code = item_["unique_code"]

        sql = """
                SELECT id, published_ts
                FROM bidding_announce
                WHERE unique_code=%s
                AND status<98
                ORDER BY id ASC
            """
        sql_2 = """
            UPDATE bidding_announce
            SET status=98
            WHERE id=%s
        """

        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, (unique_code,))
        announces = cur.fetchall()

        # 重复公告优先级排序
        none_published_ts = []
        ann = []
        for announce in announces:
            published_ts = announce["published_ts"]
            if not published_ts:
                none_published_ts.append(announce)
            else:
                if published_ts.hour == 0 and published_ts.minute == 0 and published_ts.second == 0:
                    announce["published_ts"] += datetime.timedelta(hours=23, minutes=59, seconds=59)
                ann.append(announce)
        announces = sorted(ann, key=lambda x: x["published_ts"])
        announces += none_published_ts

        for idx in range(1, len(announces)):
            if not announces[idx]["published_ts"] or \
                            announces[idx]["published_ts"] < announces[idx - 1]["published_ts"] + datetime.timedelta(
                        days=365):
                cur_2 = conn.cursor()
                cur_2.execute(sql_2, (announces[idx]["id"],))
                cur_2.close()
        cur.close()

    cnt = 0
    item = None
    for item in search_item():
        cnt += 1
        update_one(item)
        if cnt % 100 == 0:
            conn.commit()
            logger.info("update %s items id=%s" % (cnt, ""))
    if cnt % 100 != 0:
        conn.commit()
        logger.info("update %s items id=%s" % (cnt, ""))
    logger.info("update items done.")
    pass


def delete_repeat_announce_2():
    # 查询数据库
    conn = psycopg2.connect(database="crawler", user="crawler", password="1qaz2wsx",
                            host="sc-db.cfdjbes8ghlt.rds.cn-north-1.amazonaws.com.cn", port="5432")

    def search_item():
        sql = """
                SELECT id, published_ts, unique_code
                FROM bidding_announce BA
                WHERE BA.status<98
                AND BA.unique_code IN (
                    SELECT ba.unique_code
                    FROM bidding_announce ba
                    WHERE ba.status<98
                    AND ba.unique_code IS NOT NULL
                    GROUP BY ba.unique_code
                    HAVING count(*) >1
                )
                ORDER BY BA.unique_code, BA.id;
            """

        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql)

        items_, unique_code = [], None
        for item_ in cur:
            if unique_code != item_["unique_code"]:
                unique_code = item_["unique_code"]
                if items_:
                    yield items_
                    items_ = []
            items_.append(item_)
        if items_:
            yield items_

        cur.close()

    def update_one(items):
        sql_2 = """
            UPDATE bidding_announce
            SET status=98
            WHERE id=%s
        """

        announces = items

        # 重复公告优先级排序
        none_published_ts = []
        ann = []
        for announce in announces:
            published_ts = announce["published_ts"]
            if not published_ts:
                none_published_ts.append(announce)
            else:
                if published_ts.hour == 0 and published_ts.minute == 0 and published_ts.second == 0:
                    announce["published_ts"] += datetime.timedelta(hours=23, minutes=59, seconds=59)
                ann.append(announce)
        announces = sorted(ann, key=lambda x: x["published_ts"])
        announces += none_published_ts

        for idx in range(1, len(announces)):
            if not announces[idx]["published_ts"] or \
                            announces[idx]["published_ts"] < announces[idx - 1]["published_ts"] + datetime.timedelta(
                        days=365):
                cur_2 = conn.cursor()
                cur_2.execute(sql_2, (announces[idx]["id"],))
                cur_2.close()

    cnt = 0
    items = None
    for items in search_item():
        cnt += 1
        update_one(items)
        if cnt % 100 == 0:
            conn.commit()
            logger.info("update %s items id=%s" % (cnt, ""))
    if cnt % 100 != 0:
        conn.commit()
        logger.info("update %s items id=%s" % (cnt, ""))
    logger.info("update items done.")
    pass


def delete_repeat_announce_2_by_pager():
    # 查询数据库
    conn = psycopg2.connect(database="crawler", user="crawler", password="1qaz2wsx",
                            host="sc-db.cfdjbes8ghlt.rds.cn-north-1.amazonaws.com.cn", port="5432")

    def search_item(start_id, page_size, order="asc"):
        sql = """
                select id, published_ts, unique_code
                FROM bidding_announce BA
                WHERE BA.status<98
                AND BA.unique_code IN (
                    select ba.unique_code
                    from bidding_announce ba
                    WHERE ba.status<98
                    AND ba.unique_code is not NULL
                    group by ba.unique_code
                    having count(*) >1
                )
                AND BA.unique_code>%s
                ORDER BY BA.unique_code {1}, BA.id
                limit {0};
            """.format(page_size, order)

        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, (start_id,))

        items_, unique_code = [], None
        for item_ in cur:
            if unique_code != item_["unique_code"]:
                unique_code = item_["unique_code"]
                if items_:
                    yield items_
                    items_ = []
            items_.append(item_)
        # if items_:
        #     yield items_

        cur.close()

    def update_one(items):
        sql_2 = """
            UPDATE bidding_announce
            SET status=98
            WHERE id=%s
        """

        announces = items

        # 重复公告优先级排序
        none_published_ts = []
        ann = []
        for announce in announces:
            published_ts = announce["published_ts"]
            if not published_ts:
                none_published_ts.append(announce)
            else:
                if published_ts.hour == 0 and published_ts.minute == 0 and published_ts.second == 0:
                    announce["published_ts"] += datetime.timedelta(hours=23, minutes=59, seconds=59)
                ann.append(announce)
        announces = sorted(ann, key=lambda x: x["published_ts"])
        announces += none_published_ts

        for idx in range(1, len(announces)):
            if not announces[idx]["published_ts"] or \
                            announces[idx]["published_ts"] < announces[idx - 1]["published_ts"] + datetime.timedelta(
                        days=365):
                cur_2 = conn.cursor()
                cur_2.execute(sql_2, (announces[idx]["id"],))
                cur_2.close()

    cnt = 0
    items = None
    p_size = 10000
    pre_cnt = -1
    while cnt != pre_cnt:
        pre_cnt = cnt
        st_id = items[0]["unique_code"] if items else "0"
        for items in search_item(st_id, p_size):
            cnt += 1
            update_one(items)
            if cnt % 100 == 0:
                conn.commit()
                logger.info("update %s items code=%s" % (cnt, items[0]["unique_code"]))
        if cnt % 100 != 0:
            conn.commit()
            logger.info("update %s items code=%s" % (cnt, items[0]["unique_code"]))

    logger.info("fix last item")
    for items in search_item(start_id="0", page_size=1000, order="desc"):
        update_one(items)
        conn.commit()
        break

    logger.info("update items done.")
    pass


if __name__ == "__main__":
    # copy_example_announce_data()

    # compute_announce_unique_code()
    compute_announce_unique_code_by_pager()
    logger.info("compute_announce_unique_code done")
    print "\n" * 5
    delete_repeat_announce_2_by_pager()
    logger.info("delete_repeat_announce_2 done")
