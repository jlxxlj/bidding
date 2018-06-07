# coding=utf-8
# author="Jianghua Zhao"


import datetime


class Policy:
    """
    爬虫爬取策略
    """
    def __init__(self):
        pass

    # 错误处理
    # 错误1-：网页源码解析错误

    # 错误2-：抓取网页出现错误
    #     服务器错误码：404， 500， 403
    #     网络链接错误：

    # 错误3-：网页地址url映射解析方法parser错误
    #     没有找到相应的解析方法

    # 错误4-：数据库写入错误

    # 错误9-：其他错误

    # 爬虫启动策略
    # 0. 启动一个Queue负责所有的消息
    # 1. 每个省启动一个Queue负责每个省的所有消息
    # 2. 每个网站启动一个Queue负责每个网站的所有消息
    # 3. 每个源启动一个Queue负责每个源的所有消息

    START_POLICY = 2

    START_FILTER = {}

    # 每个Queue启动的爬虫数量
    CRAWLER_NUMBER = 1

    # 爬虫爬取方式
    # 1. 全量爬取
    # 2. 定时爬取
    CRAWLER_TYPE = 3

    # 时间区间
    APPLY_TIME_INTERVAL = False
    TIME_INTERVAL_ST = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    TIME_INTERVAL_ED = ""

    # 定时时长
    SCHEDULE_TIME = [h*3600 for h in range(1, 25)]
