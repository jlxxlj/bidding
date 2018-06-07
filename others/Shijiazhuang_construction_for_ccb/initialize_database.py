# coding=utf-8
# author="Jianghua Zhao"

import os
import sys
import datetime

from scpy.logger import get_logger

from daily_work import export_shijiazhuang_construction, check_new_announce
from daily_work import get_sqlite_connection

folder_path = os.path.dirname(os.path.abspath(__file__))

reload(sys)
sys.setdefaultencoding("utf-8")

logger = get_logger(__file__)


def create_table():
    conn = get_sqlite_connection()
    cur = conn.cursor()

    try:
        cur.execute("DROP TABLE announce;")
    except Exception as e:
        print e.message

    cur.execute("""
          CREATE TABLE announce(
            id INTEGER PRIMARY KEY,
            url TEXT,
            published_ts DATETIME,
            unique_code TEXT,
            start_ts DATETIME DEFAULT NULL ,
            end_ts DATETIME);
""")
    conn.commit()
    print "create table success."


def init_table():
    conn = get_sqlite_connection()
    cur = conn.cursor()

    st = datetime.datetime(year=2000, month=1, day=1)
    ed = datetime.datetime(year=2017, month=4, day=30)
    data = export_shijiazhuang_construction(st, ed)

    check_exist_sql = "select * from announce where url=(?)"
    insert_sql = "insert into announce(url, published_ts, unique_code, start_ts, end_ts) values (?,?,?,?,?)"
    cnt = 0
    for d in data:
        t = cur.execute(check_exist_sql, (d.get("url"),))
        if len(t.fetchall()) > 0:
            continue
        cur.execute(insert_sql, (d.get("url"), d.get("published_ts"), d.get("unique_code"), st, ed))
        conn.commit()
        cnt += 1
        print "processed %s" % cnt
    cur.close()
    print "init table done."


def prepare():
    create_table()
    init_table()

    dt = datetime.date(year=2017, month=5, day=1)
    ed = datetime.date(year=2017, month=6, day=29)
    while dt < ed:
        data = export_shijiazhuang_construction(dt, dt)
        check_new_announce(data, dt, dt)
        dt += datetime.timedelta(days=1)
    print "prepare done."
