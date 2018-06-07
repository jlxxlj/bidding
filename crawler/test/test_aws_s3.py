# coding=utf-8
# author="Jianghua Zhao"

import boto3
import base64
import json

import sys
sys.path.append("../")

import util
from db import aws_s3_sc
from config.config import *


def fix_bucket_sc_bidding():
    client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          region_name=AWS_REGION_NAME)

    paginator = client.get_paginator('list_objects')
    response_iterator = paginator.paginate(Bucket='sc-bidding', Prefix="quan_guo/www.chinabidding.com/2016/11/02")

    s3util = aws_s3_sc.S3Util()

    count = 0
    for page in response_iterator:
        for item in page["Contents"]:
            key = item["Key"]
            its = key.split("/")
            if len(its) == 3:
                # its[0] = "test"
                if not its[2].startswith("http"):
                    url = base64.b64decode(its[2][:-5])
                    its[2] = util.url_encode(url) + ".json"
                elif ":" in its[2]:
                    url = its[2][:-5].replace("%2f", "/")
                    url = url.replace("%2F", "/")
                    its[2] = util.url_encode(url) + ".json"
                date = "2016/10/30"
                new_key = "/".join([its[0], its[1], date, its[2]])
                obj = s3util.select("sc-bidding", condition={}, file_name=key)
                body = json.load(obj["Body"])
                s3util.insert("sc-bidding", data=body, file_name=new_key)
                s3util.delete("sc-bidding", condition={}, file_name=key)
            count += 1
            print count


def fix_china_bidding_result():
    client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          region_name=AWS_REGION_NAME)

    paginator = client.get_paginator('list_objects')
    response_iterator = paginator.paginate(Bucket='sc-bidding', Prefix="quan_guo/www.chinabidding.com/2016/11")

    s3util = aws_s3_sc.S3Util()

    import crawler
    from util import *

    bid_crawler = crawler.BidCrawler(msg_queue="fix_china_bidding_result")

    count = 0
    for page in response_iterator:
        for item in page["Contents"]:
            key = item["Key"]
            size = item["Size"]
            if size < 1000:
                obj = s3util.select("sc-bidding", condition={}, file_name=key)
                info = json.load(obj["Body"])

                # 获取需要爬取的网页地址
                if DATA_URL in info:
                    url = info[DATA_URL]
                else:
                    url = info[URL]

                # 获取与url相匹配的parser
                matched_parser = crawler.get_matched_parser(url)
                if matched_parser is None:
                    print("NO_PARSER: %s" % json.dumps(info))
                    continue
                re_url, func = matched_parser

                # 如果需要休眠，则爬虫进行休眠
                sleep_second = 2
                if sleep_second:
                    time.sleep(sleep_second)

                # 获取网页内容
                method = info.get(METHOD, "GET").upper()
                if method == "POST":
                    params = info.get(PARAMS, {})
                    html = bid_crawler.post(url, data=params, timeout=30)
                else:
                    html = bid_crawler.get(url, timeout=30)
                if html is None:
                    print("NO_CONTENT: %s" % json.dumps(info))
                    continue

                # 解析网页获取继续访问的链接和已经解析成功的公告内容
                try:
                    links, contents = func(html, info)
                except Exception, exception:
                    print("PARSER_ERROR: %s" % json.dumps(info))
                    continue

                if len(contents) == 1:
                    s3util.update("sc-bidding", condition={}, data=contents[0], upsert=True, file_name=key)
                    count += 1
                    print count
                    # print res


def test_bucket_operations():
    client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          region_name=AWS_REGION_NAME)

    paginator = client.get_paginator('list_objects')
    result = paginator.paginate(Bucket='sc-bidding', Delimiter='/')
    t = []
    for prefix in result.search('CommonPrefixes'):
        t.append(prefix.get('Prefix').split("/")[0])
    t = list(set(t))

    paginator = client.get_paginator('list_objects')
    result = paginator.paginate(Bucket='bidding', Delimiter='2016/')
    k = []
    for prefix in result.search('CommonPrefixes'):
        if prefix:
            k.append(prefix.get('Prefix').split("/")[1])
    k = list(set(k))

    o = set(t).difference(k)
    print o

    # t = ['"%s",\n' % x for x in t]
    #
    # print "".join(sorted(t))
    #
    # print len(t)

    pass


if __name__ == "__main__":
    # fix_bucket_sc_bidding()
    # fix_china_bidding_result()
    test_bucket_operations()
