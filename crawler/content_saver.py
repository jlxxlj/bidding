# coding=utf-8
# author="Jianghua Zhao"

"""
保存爬取的中标公告内容信息
"""

from scpy.date_extractor import extract_first_date
from db.db_factory import DBFactory, DBType
from util import *


class ContentSaver(object):
    def save(self, content):
        raise NotImplementedError("save_bidding_content is not implemented")


class ContentS3Saver(ContentSaver):
    def __init__(self):
        self.db_handler = DBFactory.create(DBType.AWS_S3)

    def save(self, content):
        file_name = url_encode(content[URL]) + ".json"
        origin_region = content[ORIGIN_REGION].split(">>")[0]
        region_code = BID_REGION_CODE_TABLE.get(origin_region)
        website_host = get_host_address(content[URL])

        # date = datetime.datetime.now().strftime("%Y/%m/%d")

        publish_ts = extract_first_date(content.get(PUBLISHED_TS, ""))
        if publish_ts:
            publish_date = publish_ts.strftime("%Y/%m/%d")
        else:
            publish_date = "unknown"

        file_name = "/".join(("source", region_code, website_host, publish_date, file_name))

        self.db_handler.insert(table="bidding", condition={}, data=content, upsert=True, file_name=file_name)


class ContentPostgreSQLSaver(ContentSaver):
    def __init__(self):
        self.db_handler = DBFactory.create(DBType.POSTGRESQL)

    def save(self, content):
        raise NotImplementedError("save_bidding_content is not implemented")


"""
生成保存公告内容处理方法的工厂类
"""


class ContentSaverFactory:
    def __init__(self):
        pass

    @staticmethod
    def create(db_type):
        if db_type == DBType.AWS_S3:
            return ContentS3Saver()
        elif db_type == DBType.POSTGRESQL:
            return ContentPostgreSQLSaver()
        else:
            return None
