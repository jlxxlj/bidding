# coding=utf-8
# author="Jianghua Zhao"

"""
定义爬虫任务
"""


class CrawlTask:
    # 爬虫启动策略
    # 0. 启动一个Queue负责所有的消息
    # 1. 每个省启动一个Queue负责每个省的所有消息
    # 2. 每个网站启动一个Queue负责每个网站的所有消息
    # 3. 每个源启动一个Queue负责每个源的所有消息
    START_POLICY = 2

    # 爬虫启动url源过滤
    START_FILTER = {}

    # 每个Queue启动的爬虫数量
    CRAWLER_NUMBER = 3

    # 爬虫爬取方式
    # 1. 全量爬取
    # 2. 按时间区间爬取
    # 3. 定时爬取
    CRAWLER_TYPE = 1

    # 时间区间
    TIME_INTERVAL_ST = "2001-01-01"
    TIME_INTERVAL_ED = "2016-12-31"

    # 定时时长
    SCHEDULE_TIME = [h * 3600 for h in range(1, 25)]

    def __init__(self):
        pass
