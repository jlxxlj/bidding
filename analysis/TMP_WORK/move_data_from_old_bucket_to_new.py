# coding=utf-8
# author="Jianghua Zhao"

"""
将部分招投标公告从旧的bucket迁移到新的bucket
"""

import json
from urllib import urlencode, unquote

import boto3
import re

import sys
import os

import botocore

# from boto.s3.connection import S3Connection

par_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if par_dir not in sys.path:
    sys.path.append(par_dir)

from scpy.logger import get_logger

from announce_attributes import *
from config.config import *
from db import aws_s3_sc

from scpy.date_extractor import extract_first_date

client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                      region_name=AWS_REGION_NAME)
s3_resource = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             region_name=AWS_REGION_NAME)
region_code = u"|".join(BID_REGION_CODE_TABLE.values())
reg_key = re.compile(u"^(?:%s)/.*/\d{4}/\d{1,2}/\d{1,2}/.*\.json" % region_code)
s3util = aws_s3_sc.S3Util()

logger = get_logger(__file__)


def search_item():
    paginator = client.get_paginator('list_objects')

    prefixes = ['gan_su', 'guang_dong', 'guang_xi', 'gui_zhou',
                'hai_nan', 'he_bei', 'he_nan', 'hei_long_jiang', 'hu_bei', 'hu_nan', 'ji_lin', 'jiang_su', 'jiang_xi',
                'liao_ning', 'nei_meng_gu', 'ning_xia', 'qing_hai', 'quan_guo', 'shan_dong', 'shan_xi-', 'shan_xi_',
                'shang_hai', 'si_chuan', 'tai_wan', 'tian_jin', 'xi_zhang', 'xiang_gang', 'xing_jiang', 'yun_nan',
                'zhe_jiang']

    count = 0
    for pre in prefixes:
        result = paginator.paginate(Bucket='sc-bidding', Prefix=pre)
        for pag in result:
            for item in pag.get("Contents", []):
                count += 1
                obj_key = item["Key"]

                if not reg_key.search(obj_key):
                    continue

                obj_data = s3util.select(table="sc-bidding", condition={}, file_name=obj_key)
                obj_data = json.load(obj_data["Body"])

                yield obj_data, obj_key
        pass


def url_encode(url):
    encode_url = urlencode({"url": url})[4:]
    return encode_url


def url_decode(url):
    return unquote(url)


def get_host_address(url):
    url = url.replace("http://", "")
    url = url.replace("https://", "")
    url = url.replace("?", "/")
    return url.split("/")[0]


def check_is_exists(bucket, object_key):
    exists = False
    try:
        s3_resource.Object(bucket, object_key).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            exists = False
    else:
        exists = True
    return exists


def update_item(item):
    file_name = url_encode(item[URL]) + ".json"

    if ORIGIN_REGION in item:
        region_code = BID_REGION_CODE_TABLE.get(item[ORIGIN_REGION])
    elif REGION in item:
        region_code = BID_REGION_CODE_TABLE.get(item[REGION])
    else:
        region_code = None
    if not region_code:
        return ""

    website_host = get_host_address(item[URL])

    # date = datetime.datetime.now().strftime("%Y/%m/%d")

    publish_ts = extract_first_date(item.get(PUBLISHED_TS, ""))
    if publish_ts:
        publish_date = publish_ts.strftime("%Y/%m/%d")
    else:
        publish_date = "unknown"

    file_name = "/".join(("source", region_code, website_host, publish_date, file_name))

    if not check_is_exists(bucket="bidding", object_key=file_name):
        s3util.insert(table="bidding", condition={}, data=item, upsert=True, file_name=file_name)
    # else:
    #     print "exists key (%s) " % file_name

    return file_name


def move_data():
    cnt = 0
    obj_key, key = "", ""
    for item, key in search_item():
        cnt += 1
        obj_key = update_item(item)
        if cnt % 1000 == 0:
            logger.info("moved %s items (%s to %s)" % (cnt, key, obj_key))
    if cnt % 1000 == 0:
        logger.info("moved %s items (%s to %s)" % (cnt, key, obj_key))
    logger.info("moved done")


#
# def move_data_2():
#     conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
#
#     srcBucket = conn.get_bucket("sc-bidding")
#     dstBucket = conn.get_bucket("bidding")
#
#     cnt = 0
#     obj_key = ""
#     for item in search_item():
#         cnt += 1
#         obj_key = update_item(item)
#         if cnt % 1000 == 0:
#             logger.info("moved %s items (%s)" % (cnt, obj_key))
#     if cnt % 1000 == 0:
#         logger.info("moved %s items (%s)" % (cnt, obj_key))
#     logger.info("moved done")


if __name__ == "__main__":
    # reg_code = BID_REGION_CODE_TABLE.values()
    # reg_code.sort()
    # print reg_code
    move_data()
