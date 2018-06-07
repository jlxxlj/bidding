# coding=utf-8
# author="Jianghua Zhao"

import psycopg2
from psycopg2.extras import RealDictCursor
from scpy.logger import get_logger

import sys
import os

par_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if par_dir not in sys.path:
    sys.path.append(par_dir)

from toolkit.location_complement import search_full_region, get_full_region_name

logger = get_logger(__file__)


def complement_region():
    # 查询数据库
    conn = psycopg2.connect(database="sc_crawler", user="sc_crawler", password="1qaz2wsx",
                            host="114.55.28.251", port="5432")

    def search_item():
        sql = """
            SELECT id, region
            from bidding_announce
        """
        # WHERE province is NULL AND city is NULL AND county is NULL;
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql)
        for item_ in cur.fetchall():
            yield item_

    def update_one(item_):
        _id = item_["id"]
        region = item_["region"]
        if region:
            region = region.decode("utf-8")
            full_region = search_full_region(region)
            if not full_region:
                full_region = {}
            # full_region_name = get_full_region_name(full_region)
            province = full_region.get("province")
            city = full_region.get("city")
            county = full_region.get("county")

            sql = """
                UPDATE bidding_announce
                SET province=%s, city=%s, county=%s
                WHERE id=%s
            """
            cur = conn.cursor()
            cur.execute(sql, (province, city, county, _id))
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


def complement_region_by_pager():
    # 查询数据库
    conn = psycopg2.connect(database="sc_crawler", user="sc_crawler", password="1qaz2wsx",
                            host="114.55.28.251", port="5432")

    def search_item(start_id, page_size):
        sql = """
            SELECT id, region
            from bidding_announce
            WHERE id>%s
            ORDER BY id
            limit {0}
        """.format(page_size)
        # WHERE province is NULL AND city is NULL AND county is NULL;
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, (start_id,))
        for item_ in cur.fetchall():
            yield item_

    def update_one(item_):
        _id = item_["id"]
        region = item_["region"]
        if region:
            region = region.decode("utf-8")
            full_region = search_full_region(region)
            if not full_region:
                full_region = {}
            # full_region_name = get_full_region_name(full_region)
            province = full_region.get("province")
            city = full_region.get("city")
            county = full_region.get("county")

            sql = """
                UPDATE bidding_announce
                SET province=%s, city=%s, county=%s
                WHERE id=%s
            """
            cur = conn.cursor()
            cur.execute(sql, (province, city, county, _id))
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
            if cnt % 1000 == 0:
                conn.commit()
                logger.info("update %s items id=%s" % (cnt, item["id"]))
        if cnt % 1000 != 0:
            conn.commit()
            logger.info("update %s items id=%s" % (cnt, item["id"]))
    logger.info("update items done.")


if __name__ == "__main__":
    complement_region_by_pager()
