# coding=utf-8
# author="Jianghua Zhao"

import sys
import os
import json
import re

padir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if padir not in sys.path:
    sys.path.append(padir)

import page_start
from crawler import BidCrawler
from queue import publish_message, clear_queue
from util import *


def print_green(arg):
    print "\033[1;32;40m%s\033[0m" % str(arg)


def print_red(arg):
    print "\033[1;31;40m%s\033[0m" % str(arg)


def show_start_url(item):
    dc = {}
    for k in item.keys():
        if k in (WEBSITE, URL, ORIGIN_REGION, METHOD):
            dc[k] = item[k]
    return json.dumps(dc).decode("unicode-escape")


def skip_urls(urls, skips):
    result = []
    for item in urls:
        mark = False
        for skp in skips:
            if skp in item[URL]:
                mark = True
                break
        if mark is False:
            result.append(item)
    return result


def fix_urls(urls, fixes):
    if not fixes:
        return urls

    result = []
    for item in urls:
        mark = False
        for fix in fixes:
            if fix in item[URL]:
                mark = True
                break
        if mark is True:
            result.append(item)
    return result


def filter_with(urls, filter_arguments):
    origin = filter_arguments.get(ORIGIN_REGION)
    if origin:
        result = []
        for item in urls:
            if origin in item.get(ORIGIN_REGION):
                result.append(item)

        # result, res = [], result
        # for item in urls:
        #     if item not in res:
        #         result.append(item)

        return result
    return urls


def filter_without(urls, filter_arguments):
    origin = filter_arguments.get(ORIGIN_REGION)
    if origin:
        result = []
        for item in urls:
            if origin in item.get(ORIGIN_REGION):
                result.append(item)

        result, res = [], result
        for item in urls:
            if item not in res:
                result.append(item)

        return result
    return urls


def test_start_urls():
    skips = [
        "www.chinabidding.com",
        "cz.fjzfcg.gov.cn",
    ]
    fixes = [
        'cqjbjyzx',
        'fjjyzx'
    ]

    urls = skip_urls(page_start.start_urls, skips)
    # urls = fix_urls(urls, fixes)
    urls = filter_with(urls, {ORIGIN_REGION: u"重庆"})
    # urls = filter_without(urls, {ORIGIN_REGION: u"重庆"})

    queue_name = "test_start_urls"
    success_list, fail_list = [], []
    for i, item in enumerate(urls):
        print "%d:\t" % i, "test start url: ", show_start_url(item)
        clear_queue(queue_name)
        publish_message(queue_name, item)
        bid_crawler = BidCrawler(queue_name, skip_parse_failure=True)
        results = []
        for k in range(10):
            res, info = bid_crawler.crawl()
            if res is "NO_MESSAGE":
                break
            if res is not "SUCCESS":
                results.append("%s: %s" % (k, res))
        if len(results) != 0:
            print_red("crawl start url failed: ")
            print_green(results)
            fail_list.append(item)
        else:
            success_list.append(item)

    print "\nTotal success urls are %s: " % len(success_list)
    for i, item in enumerate(success_list):
        print "%3d: %s" % (i, show_start_url(item))

    print_red("\nTotal fail urls are %s: " % len(fail_list))
    for i, item in enumerate(fail_list):
        print_red("%3d: %s" % (i, show_start_url(item)))

    import util
    hosts = set()
    for item in success_list:
        host = util.get_host_address(item.get("url"))
        hosts.add(host)
    hosts = sorted(hosts)
    print "\nAvailable Hosts:"
    for host in hosts:
        print '"%s",' % host


if __name__ == "__main__":
    test_start_urls()
