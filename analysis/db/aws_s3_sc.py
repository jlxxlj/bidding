# coding=utf-8
# author="Jianghua Zhao"

import boto3
import json

from config.config import *
from db_sc import DBInterface


def get_aws_service(service_name):
    aws_session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                region_name=AWS_REGION_NAME)
    return aws_session.resource(service_name=service_name)


def get_aws_client(client_name):
    aws_session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                region_name=AWS_REGION_NAME)
    return aws_session.client(client_name)


class S3Util(DBInterface):
    def __init__(self):
        super(S3Util, self).__init__()
        self.s3 = get_aws_service('s3')

    def create(self, bucket):
        bucket_config = {'LocationConstraint': 'cn-north-1'}
        self.s3.create_bucket(Bucket=bucket, CreateBucketConfiguration=bucket_config)

    # 插入
    def insert(self, table, data, **kwargs):
        file_name = kwargs.get("file_name")
        if not file_name:
            raise Exception("the file name is not specified")

        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False)
        data += "\n"  # 添加换行符，方便后续spark处理
        self.s3.Object(table, file_name).put(Body=data)

    # 查找
    def select(self, table, condition, **kwargs):
        file_name = kwargs.get("file_name")
        if not file_name:
            raise Exception("the file name is not specified")

        return self.s3.Object(table, file_name).get()

    # 删除
    def delete(self, table, condition, **kwargs):
        file_name = kwargs.get("file_name")
        if not file_name:
            raise Exception("the file name is not specified")

        self.s3.Object(table, file_name).delete()

    # 修改
    def update(self, table, condition, data, upsert=False, **kwargs):
        self.delete(table, condition, **kwargs)
        self.insert(table, data, **kwargs)


if __name__ == "__main__":
    s3 = S3Util()
    s3.insert("sc-bidding", data={"content": "hello world!"}, file_name="www.ccgp.gov.cn/test.txt")
    RES = s3.select("sc-bidding", {}, file_name="www.ccgp.gov.cn/test.txt")
    s3.delete("sc-bidding", {}, file_name="www.ccgp.gov.cn/test.txt")
    print RES
