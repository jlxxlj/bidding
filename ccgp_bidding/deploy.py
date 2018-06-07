#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from fabric.api import env, execute, parallel, settings, run, put, cd, sudo

reload(sys)
sys.setdefaultencoding("utf-8")

REMOTE_PATH = "/usr/app/python/bid_crawlers/sc-bidding"


def start_update_service(path):
    with settings(warn_only=True):
        path += "/tornado-service"
        with cd(path):
            run('$(nohup python tornado_service.py 1>/dev/null 2>&1 &) && sleep 1')


@parallel(pool_size=10)
def deploy_all(number):
    with settings(warn_only=True):
        run('rm -rf ' + REMOTE_PATH + "*")

    run("mkdir -p " + REMOTE_PATH)
    put("~/PycharmProjects/sc-bidding/*", REMOTE_PATH)

    start_update_service(REMOTE_PATH)

    for i in range(number):
        path = REMOTE_PATH + "_" + str(i)
        run('cp -R ' + REMOTE_PATH + ' ' + path)
        with cd(path):
            run('$(nohup python monitor.py 1>/dev/null 2>&1 &) && sleep 1')


if __name__ == "__main__":
    env.password = 'zhao513975'
    env.hosts = [
        "jianghua.zhao@120.55.81.205"
    ]
    execute(deploy_all, 1)
