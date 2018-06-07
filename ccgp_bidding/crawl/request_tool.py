#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import os
import time
import requests

from scpy.request_util import get_random_ua
from scpy.logger import get_logger

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

HEADERS = {"User-Agent": get_random_ua()}
session = requests.session()
logger = get_logger(__file__)

TIMEOUT = 20
CHANTE_TIMES = 5


def make_request(url, params, method):
    for times in range(CHANTE_TIMES):
        method = method.upper()
        if method == 'GET':
            try:
                # session.proxies = {"http": "http://106.38.251.63:8088"}
                response = session.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
            except Exception, e:
                logger.info('exceptin requests')
                continue

        elif method == "POST":
            response = session.post(url, data=params, headers=HEADERS, timeout=TIMEOUT)
        else:
            raise Exception('request method error must GET or POST')

        if response.status_code != 200:
            logger.info("response status_code {0}".format(response.status_code))
            change_ip()
            logger.info('change ip')
            time.sleep(5)
            continue
        return response


def change_ip():
    os.system('sh changeIp.sh')


firefox_bin = "/usr/lib/firefox/firefox"
firefox_driver = None
def selenium_request(url, method="GET", params={}):
    global firefox_driver

    if firefox_driver is None:
        firefox_driver = webdriver.Firefox(executable_path=firefox_bin, firefox_binary=FirefoxBinary(firefox_bin))
    firefox_driver.get(url)
    html = firefox_driver.page_source
    return html
