#!/usr/bin/env python
# encoding=utf-8

from scpy.xawesome_codechecker import get_ip

"""
全局常量（aws）
"""
__author__ = 'xlzd'

# [server]
DEBUG = False
WORKERS = 8

# [postgres]
# PG_HOST = 'sc-db.cfdjbes8ghlt.rds.cn-north-1.amazonaws.com.cn'
PG_HOST = 'sc-db-read-only.cfdjbes8ghlt.rds.cn-north-1.amazonaws.com.cn'
PG_PORT = '5432'

SC_CRAWLER_PG_QUERY = {
    "user": "crawler",
    "password": "1qaz2wsx",
    "database": "crawler"
}

# 当API查询不到的时候放入PG中
MISS_API_PG_QUERY = {
    "user": "crawler_log",
    "password": "!QAZ@WSX",
    "database": "crawler_log",
    # "table": "missing_company",
}
