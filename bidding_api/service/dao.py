#!/usr/bin/env python
# encoding=utf-8

"""
数据库查询接口
"""
import sys
import os
from scpy.logger import get_logger

LOGGER = get_logger()
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from config import PG_HOST, PG_PORT, SC_CRAWLER_PG_QUERY

sc_crawler_pg_cnn_pool = pool.ThreadedConnectionPool(minconn=1, maxconn=20, host=PG_HOST, port=PG_PORT,
                                                     **SC_CRAWLER_PG_QUERY)


def sc_crawler_insert_one(pg_sql, data=None):
    conne = sc_crawler_pg_cnn_pool.getconn()
    try:
        cursor = conne.cursor()
        if data:
            cursor.execute(pg_sql, data)
        else:
            cursor.execute(pg_sql)
    except Exception, e:
        LOGGER.error(e)
        cursor.close()
        conne.rollback()
    else:
        cursor.close()
        conne.commit()
    finally:
        sc_crawler_pg_cnn_pool.putconn(conne)


def sc_crawler_query_all(pg_query, data=None):
    import json
    LOGGER.info("Get conn")
    conne = sc_crawler_pg_cnn_pool.getconn()
    LOGGER.info("Start query")
    # LOGGER.info(pg_query)
    LOGGER.info(json.dumps(data, indent=4).decode("unicode-escape"))
    result_list = []
    try:
        cursor = conne.cursor(cursor_factory=RealDictCursor)
        if data:
            cursor.execute(pg_query, data)
        else:
            cursor.execute(pg_query)
        for row in cursor.fetchall():
            result_list.append(row)
    except Exception, e:
        LOGGER.error(e)
        cursor.close
        conne.rollback()
    else:
        cursor.close()
        conne.commit()
    finally:
        sc_crawler_pg_cnn_pool.putconn(conne)
    LOGGER.info("Done query")
    return result_list


def sc_crawler_query_many(pg_query, data=None, cnt=1):
    conn = sc_crawler_pg_cnn_pool.getconn()
    result_list = []
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        if data:
            cursor.execute(pg_query, data)
        else:
            cursor.execute(pg_query)
        result_list = cursor.fetchmany(cnt)
    except Exception, e:
        LOGGER.error(e)
        cursor.close()
        conn.rollback()
    else:
        cursor.close()
        conn.commit()
    finally:
        sc_crawler_pg_cnn_pool.putconn(conn)
    return result_list


def sc_crawler_query_one(pg_query, data=None):
    result = sc_crawler_query_many(pg_query, data, cnt=1)
    if result:
        return result[0]


def sc_crawler_non_query(pg_non_query):
    conn = sc_crawler_pg_cnn_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute(pg_non_query)
    except Exception, e:
        LOGGER.error(e)
        cursor.close()
        conn.rollback()
    else:
        cursor.close()
        conn.commit()
    finally:
        sc_crawler_pg_cnn_pool.putconn(conn)
