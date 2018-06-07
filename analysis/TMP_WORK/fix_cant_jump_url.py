# coding=utf-8
# author="Jianghua Zhao"

"""
修复 重庆市政府采购网 公告地址不能访问的问题
"""
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from scpy.logger import get_logger

import sys
import os

par_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if par_dir not in sys.path:
    sys.path.append(par_dir)

logger = get_logger(__file__)


def fix_cant_jump_url():
    # 查询数据库
    conn = psycopg2.connect(database="sc_crawler", user="sc_crawler", password="1qaz2wsx",
                            host="114.55.28.251", port="5432")

    def search_item():
        sql = """
            SELECT id, url
            from bidding_announce
            WHERE url LIKE 'https://www.cqgp.gov.cn/notices/%'
        """
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql)
        for item_ in cur.fetchall():
            yield item_

    def update_one(item_):
        _id = item_["id"]
        url = item_["url"]
        if url and "detail" not in url:
            new_url = url.replace("https://www.cqgp.gov.cn/notices/", "https://www.cqgp.gov.cn/notices/detail/")

            sql = """
                UPDATE bidding_announce
                SET url=%s
                WHERE id=%s
            """
            cur = conn.cursor()
            cur.execute(sql, (new_url, _id))
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


# 修改s3中的中标公告
from announce_attributes import *
from db import aws_s3_sc
# Get the service resource
s3util = aws_s3_sc.S3Util()
s3_client = aws_s3_sc.get_aws_client("s3")


def save(content):
    def url_encode(url):
        encode_url = urlencode({"url": url})[4:]
        return encode_url

    def url_decode(url):
        return unquote(url)

    def get_host_address(url):
        url = url.replace("http://", "")
        url = url.replace("https://", "")
        url = url.replace("?", "/")
        return url.split("/")[0]

    from scpy.date_extractor import extract_first_date

    file_name = url_encode(content[URL]) + ".json"
    region_code = BID_REGION_CODE_TABLE.get(content[ORIGIN_REGION])
    website_host = get_host_address(content[URL])

    # date = datetime.datetime.now().strftime("%Y/%m/%d")

    publish_ts = extract_first_date(content.get(PUBLISHED_TS, ""))
    if publish_ts:
        publish_date = publish_ts.strftime("%Y/%m/%d")
    else:
        publish_date = "unknown"

    file_name = "/".join(("source", region_code, website_host, publish_date, file_name))

    s3util.insert(table="bidding", condition={}, data=content, upsert=True, file_name=file_name)


def fix_s3_cant_jump_url():
    paginator = s3_client.get_paginator('list_objects')

    response_iterator = paginator.paginate(
        Bucket='bidding',
        Prefix='source/chong_qing/www.cqgp.gov.cn',
    )

    cnt, p_cnt = 0, 0
    for page in response_iterator:
        for item in page.get("Contents", []):
            cnt += 1
            object_key = item["Key"]
            if "detail" not in object_key:
                p_cnt += 1
                obj = s3util.select(table="bidding", condition={}, file_name=object_key)
                s3_data = json.loads(obj["Body"].read())
                s3_data["url"] = s3_data["url"].replace("https://www.cqgp.gov.cn/notices/",
                                                        "https://www.cqgp.gov.cn/notices/detail/")
                save(s3_data)
                s3util.delete(table="bidding", condition={}, file_name=object_key)
                logger.info("find %s, processed %s" % (cnt, p_cnt))


if __name__ == "__main__":
    # fix_cant_jump_url()
    fix_s3_cant_jump_url()
