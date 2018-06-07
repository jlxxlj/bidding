# coding=utf-8
# author="Jianghua Zhao"

"""
修复没有中标公告类型的错误
"""


import re

import psycopg2

from psycopg2.extras import RealDictCursor
from scpy.logger import get_logger

logger = get_logger(__file__)

url_type_map = []


def url_filter(url, *args):
    re_keyword = "\\.-?()"
    for item in re_keyword:
        url = url.replace(item, "\\" + item)
    url = url % args
    return url


def add_map(announce_type, url_pattern):
    url_type_map.append({
        "announce_type": announce_type,
        "url_pattern": url_pattern
    })


def get_announce_type_by_url(url):
    for url_type in url_type_map:
        if re.search(url_type["url_pattern"], url):
            return url_type["announce_type"]
    return u"中标公告"


def url_announce_type_map():
    add_map(announce_type=u"中标公告",
            url_pattern=url_filter("http://www.gxzfcg.gov.cn/view/staticpags/shengji_zbgg"))
    add_map(announce_type=u"成交公告",
            url_pattern=url_filter("http://www.gxzfcg.gov.cn/view/staticpags/shengji_cjgg"))
    add_map(announce_type=u"中标公告",
            url_pattern=url_filter("http://www.gxzfcg.gov.cn/view/staticpags/sxjcg_zbgg"))
    add_map(announce_type=u"成交公告",
            url_pattern=url_filter("http://www.gxzfcg.gov.cn/view/staticpags/sxjcg_cjgg"))

    add_map(announce_type=u"中标公告",
            url_pattern=url_filter("http://www.gxgp.gov.cn"))

    add_map(announce_type=u"中标公告",
            url_pattern=url_filter("http://www.xzzbtb.gov.cn"))

    add_map(announce_type=u"成交公告",
            url_pattern=url_filter("http://zfcg.xjcz.gov.cn"))

    add_map(announce_type=u"中标成交公告",
            url_pattern=url_filter("http://www.nmgzfcg.gov.cn/"))

    add_map(announce_type=u"成交公告",
            url_pattern=url_filter("http://www.hainan.gov.cn"))

    add_map(announce_type=u"中标公告",
            url_pattern=url_filter("http://www.gdgpo.gov.cn"))

    add_map(announce_type=u"采购结果公告",
            url_pattern=url_filter("http://www.yngp.com"))

    add_map(announce_type=u"中标公示",
            url_pattern=url_filter("http://www.gzzbw.cn"))

    add_map(announce_type=u"中标公告",
            url_pattern=url_filter("http://www.ccgp-qinghai.gov.cn"))

    add_map(announce_type=u"中标公告",
            url_pattern=url_filter("http://www.gszfcg.gansu.gov.cn"))

    add_map(announce_type=u"结果公告",
            url_pattern=url_filter("http://www.sczfcg.com/view/staticpags/jggg"))
    add_map(announce_type=u"成交公告",
            url_pattern=url_filter("http://www.sczfcg.com/view/staticpags/shiji_jggg"))

    add_map(announce_type=u"中标公告",
            url_pattern=url_filter("http://jx.hzzhaobiao.com"))

    add_map(announce_type=u"中标公告",
            url_pattern=url_filter("http://cz.fjzfcg.gov.cn"))

    add_map(announce_type=u"中标公告",
            url_pattern=url_filter("http://www.ccgp-anhui.gov.cn"))
    pass


def fix_announce_type():
    # 查询数据库
    conn = psycopg2.connect(database="sc_crawler", user="sc_crawler", password="1qaz2wsx",
                            host="114.55.28.251", port="5432")

    def search_item():
        sql = "SELECT id, url from bidding_announce WHERE announce_type is NULL limit 100"
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql)
        for item_ in cur.fetchall():
            yield item_

    def update_one(item_):
        cur = conn.cursor()
        _id = item_["id"]
        url = item_["url"]
        announce_type = get_announce_type_by_url(url)
        sql = u"UPDATE bidding_announce SET announce_type=%s WHERE id=%s "
        cur.execute(sql, (announce_type, _id))
        cur.close()

    cnt = 0
    item = None
    for it in search_item():
        item = it
        update_one(item)
        cnt += 1
        if cnt % 500 == 0:
            conn.commit()
            logger.info("update %s items id=%s" % (cnt, item["id"]))
    if cnt % 500 != 0:
        conn.commit()
        logger.info("update %s items id=%s" % (cnt, item["id"]))
    logger.info("update items done.")

    pass


if __name__ == "__main__":
    fix_announce_type()
