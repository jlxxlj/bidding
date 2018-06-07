#!/usr/bin/env python
# -*-coding:utf-8-*-

__author__ = "wu.zheng"

from conf import config
from psycopg2.pool import ThreadedConnectionPool
from singleton import Singleton
from psycopg2.extras import DictCursor, RealDictCursor

import sys

sys.path.append("..")


class PgUtil():
    __metaclass__ = Singleton

    def __init__(self):
        self.conn_pool = ThreadedConnectionPool(
            minconn=4,
            maxconn=100,
            database=config.POSTGRESQL_DATABASE,
            user=config.POSTGRESQL_USER_NAME,
            password=config.POSTGRESQL_PASSWORD,
            host=config.POSTGRESQL_HOST,
            port=config.POSTGRESQL_PORT
        )

    def get_conn(self):
        conn = self.conn_pool.getconn()
        return conn

    def put_conn(self, conn):
        self.conn_pool.putconn(conn)

    def query_all_sql(self, sql):
        conn = self.get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql)
        result_list = []
        for row in cur.fetchall():
            result_list.append(row)
        conn.commit()
        self.put_conn(conn)
        return result_list

    def query_one_sql(self, sql):
        conn = self.get_conn()
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute(sql)
        row = cur.fetchone()
        cur.close()
        conn.commit()
        self.put_conn(conn)
        return dict(row) if row else {}

    def execute_sql(self, sql):
        conn = self.get_conn()
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute(sql)
        cur.close()
        conn.commit()
        self.put_conn(conn)

    def execute_insert_sql(self, sql, values):
        conn = self.get_conn()
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute(sql, values)
        cur.close()
        conn.commit()
        self.put_conn(conn)


if __name__ == '__main__':
    sql_request = '''select dimension, id from dimension where category='法务' or category='失信' or category='执行' '''
    pg = PgUtil()
    map_id = {}
    import json
    import time

    for index in range(100):
        for row in pg.query_all_sql(sql_request):
            data_row = {row['dimension']: row['id']}
            map_id.update(data_row)
        time.sleep(1)
        print json.dumps(map_id, ensure_ascii=False)
