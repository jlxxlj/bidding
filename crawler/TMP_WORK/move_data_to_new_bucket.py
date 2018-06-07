# coding=utf-8
# author="Jianghua Zhao"

import sys
import os
import json

from db import aws_s3_sc

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import content_saver


def move_data_to_new_bucket(src_bucket, dst_bucket):
    s3util = aws_s3_sc.S3Util()
    s3_client = aws_s3_sc.get_aws_client("s3")

    saver = content_saver.ContentS3Saver()

    paginator = s3_client.get_paginator('list_objects')
    response_iterator = paginator.paginate(
        Bucket=src_bucket,
        Prefix='',
    )

    count = 0
    for page in response_iterator:
        for item in page["Contents"]:
            object_key = item["Key"]

            obj = s3util.select(table=src_bucket, condition={}, file_name=object_key)
            s3_data = json.loads(obj["Body"].read())

            saver.save(s3_data)
            # s3util.delete(table=src_bucket, condition={}, file_name=object_key)

            count += 1
            if count % 1000 == 0:
                print "::%8d items has been moved" % count

    print "::%8d items has been moved" % count
    print "move_data_to_new_bucket done!"


if __name__ == "__main__":
    move_data_to_new_bucket(src_bucket="sc-bidding", dst_bucket="bidding")
