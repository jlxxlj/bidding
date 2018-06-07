# coding=utf-8
# author="Jianghua Zhao"

import sys

from pymongo import MongoClient
from config import config

from db_sc import DBInterface

reload(sys)
sys.setdefaultencoding('utf-8')


class MongoUtil(DBInterface):
    def __init__(self, ):
        self.conn = MongoClient(host=config.MONGO_HOST, port=config.MONGO_PORT)
        self.db = self.conn[config.MONGO_DB_NAME]

    # 插入
    def insert(self, table, data, **kwargs):
        self.db[table].insert(data)

    # 查找
    def select(self, table, condition, **kwargs):
        result = []
        for item in self.db[table].find(condition):
            result.append(item)
        return result

    # 删除
    def delete(self, table, condition, **kwargs):
        self.db[table].delete_many(condition)

    # 修改
    def update(self, table, condition, data, upsert=False, **kwargs):
        self.db[table].update(condition, data, upsert=upsert)


