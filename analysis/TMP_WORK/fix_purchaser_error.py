# coding=utf-8
# author="Jianghua Zhao"

"""
修复采购单位是 ‘采购单位’ 的错误
"""


import psycopg2
from psycopg2.extras import RealDictCursor
from scpy.logger import get_logger

import sys
import os

par_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if par_dir not in sys.path:
    sys.path.append(par_dir)

logger = get_logger(__file__)

from announce_analysis import *


def fix_purchaser_error():
    # 查询数据库
    conn = psycopg2.connect(database="sc_crawler", user="sc_crawler", password="1qaz2wsx",
                            host="114.55.28.251", port="5432")

    s3util = aws_s3_sc.S3Util()

    def search_item():
        # sql = """
        #     SELECT id, content_source
        #     from bidding_announce
        #     WHERE purchaser='采购单位'
        #     AND content_source IS NOT NULL ;
        # """
        sql = """
            SELECT id, content_source
            from bidding_announce
            WHERE id=1599858;
        """
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql)
        for item_ in cur.fetchall():
            yield item_

    def update_one(item_):
        _id = item_["id"]
        object_key = item_["content_source"].replace("s3:bidding:", "", 1)
        if object_key:
            print "\n", object_key
            try:
                obj = s3util.select(table="bidding", condition={}, file_name=object_key)
                s3_data = json.loads(obj["Body"].read())
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                logger.exception(e)
                return

            # 分析数据
            try:
                announce_data = analysis(s3_data)
            except Exception as e:
                logger.exception(e)
                new_name = "parse_error/" + urllib.urlencode({"name": object_key})[5:]
                s3util.insert(table="bidding", data=s3_data, file_name=new_name)
                return
            # 存库
            content_source = "s3:bidding:" + object_key
            save_bidding_result(json.dumps(announce_data), content_source)

    cnt = 0
    item = None
    for item in search_item():
        cnt += 1
        update_one(item)
        if cnt % 10 == 0:
            conn.commit()
            logger.info("update %s items id=%s" % (cnt, item["id"]))
    if cnt % 10 != 0:
        conn.commit()
        logger.info("update %s items id=%s" % (cnt, item["id"]))
    logger.info("update items done.")


if __name__ == "__main__":
    fix_purchaser_error()
