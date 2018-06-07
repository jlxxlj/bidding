# coding=utf-8
# author="Jianghua Zhao"


class DBType:
    MONGO = "mongo"
    POSTGRESQL = "postgresql"
    AWS_S3 = "aws_s3"


class DBFactory(object):
    def __init__(self):
        pass

    @staticmethod
    def create(db_type):
        if db_type == DBType.MONGO:
            import mongo_sc
            return mongo_sc.MongoUtil()

        elif db_type == DBType.POSTGRESQL:
            import postgresql_sc
            return postgresql_sc.PostgresqlUtil()

        elif db_type == DBType.AWS_S3:
            import aws_s3_sc
            return aws_s3_sc.S3Util()

        else:
            return None
