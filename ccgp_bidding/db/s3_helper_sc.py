# coding=utf-8
# author="Jianghua Zhao"

import boto3
import datetime
import json
from scpy.logger import get_logger

LOGGER = get_logger()


def get_aws_service(service_name):
    aws_session = boto3.Session(aws_access_key_id="AKIAPQSZXOZS5YSMKLIQ",
                                aws_secret_access_key="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",
                                region_name="cn-north-1")
    return aws_session.resource(service_name=service_name)


class S3Util():
    def __init__(self):
        self.s3 = get_aws_service('s3')
        self.bucket = 'sc-bidding'

    def create(self, bucket):
        bucket_config = {'LocationConstraint': 'cn-north-1'}
        self.s3.create_bucket(Bucket=bucket, CreateBucketConfiguration=bucket_config)

    def insert(self, bucket, data):
        file_name = data.get("file_name")

        if not file_name:
            raise Exception("the file name is not specified")
        else:
            del data["file_name"]

        try:
            data = json.dumps(data, ensure_ascii=False)
            self.s3.Object(bucket, file_name).put(Body=data)
        except Exception, e:
            LOGGER.error(e)

    def update(self, bucket, condition, data, upsert):
        try:
            self.delete(bucket, condition)
            data.update(condition)
            self.insert(bucket, data)
        except Exception, e:
            LOGGER.error(e)

    def delete(self, bucket, condition):
        file_name = condition.get("file_name")

        if not file_name:
            raise Exception("the file name is not specified")

        try:
            self.s3.Object(bucket, file_name).delete()
        except Exception, e:
            LOGGER.error(e)

    def select(self, bucket, condition):
        file_name = condition.get("file_name")

        if not file_name:
            raise Exception("the file name is not specified")

        try:
            return self.s3.Object(bucket, file_name).get()
        except Exception, e:
            LOGGER.error(e)


if __name__ == "__main__":
    s3 = S3Util()
    s3.insert("sc-bidding", {"file_name": "test.json", "content": "hello world!"})
    RES = s3.select("sc-bidding", {"file_name": "test2.json"})
    s3.delete("sc-bidding", {"file_name": "test2.json"})
