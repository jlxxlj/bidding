# coding=utf-8
# author="Jianghua Zhao"


import mongo_sc
import postgresql_sc
import s3_helper_sc
# import cassandra_sc

from conf import config


class DBType:
    MONGO = "MONGO"
    POSTGRESQL = "POSTGRESQL"
    CASSANDRA = "CASSANDRA"
    S3 = "S3"


class DBHelper():
    """
    定义统一的数据存储接口
    """

    def __init__(self, db, table=None):
        self.db = db
        if self.db == DBType.MONGO:
            self.db_util = mongo_sc.MongoUtil()
        elif self.db == DBType.POSTGRESQL:
            self.db_util = postgresql_sc.PostgresqlUtil()
        elif self.db == DBType.CASSANDRA:
            # self.db_util = cassandra_sc.CassandraUtil()
            self.db_util = None
        elif self.db == DBType.S3:
            self.db_util = s3_helper_sc.S3Util()
        else:
            raise Exception("there is no database %" % db)
        self.table = table

    def insert(self, table, data):
        self.db_util.insert(table, data)

    def update(self, table, condition, data, upsert):
        self.db_util.update(table, data, condition, upsert)

    def delete(self, table, condition):
        self.db_util.delete(table, condition)

    def select(self, table, condition):
        return self.db_util.select(table, condition)
