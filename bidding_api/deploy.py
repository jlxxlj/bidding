# !/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import argparse

from fabric.api import *
from fabric.contrib.files import exists

BASE_PATH = '/usr/app/python/'
TAR_FILE = 'bidding-api.tar.gz'
APP_PATH = BASE_PATH + 'bidding-api'
APP_NAME = 'bidding_api.py'


def pack_codes():
    with settings(warn_only=True):
        local("rm -f */*.pyc", shell='/bin/bash')
        local("tar -zcf {fname} *".format(fname=TAR_FILE), shell='/bin/bash')


def del_packed_codes():
    if os.path.exists(TAR_FILE):
        local("rm {fname}".format(fname=TAR_FILE), shell='/bin/bash')


@parallel(10)
def deploy_app():
    if not exists(APP_PATH):
        run('mkdir -p ' + APP_PATH)
    with settings(warn_only=True):
        sudo('rm -Rf ' + APP_PATH + '/*')
    put(TAR_FILE, APP_PATH + '/')
    with cd(APP_PATH):
        run('tar -zxf ' + TAR_FILE, shell='/bin/bash')
        run('rm ' + TAR_FILE, shell='/bin/bash')


@parallel(10)
def run_app():
    with settings(warn_only=True):
        sudo('pkill -f ' + APP_NAME)
    with cd(APP_PATH):
        run('sleep 2')
        run('$(nohup python {app} 7001 >& /dev/null < /dev/null &) && sleep 1'.format(app=APP_NAME),
            shell='/bin/bash')


@parallel(10)
def run_app_test():
    app_name_test = APP_NAME.replace(".py", "_test.py")
    with settings(warn_only=True):
        sudo('pkill -f ' + app_name_test)
    with cd(APP_PATH):
        run("cp {fname} {tfname}".format(fname=APP_NAME, tfname=app_name_test))
        run('sleep 2')
        run('$(nohup python {app} 12532 >& /dev/null < /dev/null &) && sleep 1'.format(app=app_name_test),
            shell='/bin/bash')


@parallel(10)
def run_app_dev():
    app_name_test = APP_NAME.replace(".py", "_dev.py")
    with settings(warn_only=True):
        sudo('pkill -f ' + app_name_test)
    with cd(APP_PATH):
        run("cp {fname} {tfname}".format(fname=APP_NAME, tfname=app_name_test))
        run('sleep 2')
        run('$(nohup python {app} 12535 >& /dev/null < /dev/null &) && sleep 1'.format(app=app_name_test),
            shell='/bin/bash')


@parallel(10)
def kill_all():
    with settings(warn_only=True):
        run('pkill -f python')


def get_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-t", "--test", action="store_true", help="Deploy test mode")
    arg_parser.add_argument("-d", "--dev", action="store_true", help="Deploy develop mode")
    return arg_parser.parse_args()


if __name__ == "__main__":
    env.hosts = [
        "52.80.80.32",
    ]
    env.user = "ubuntu"
    env.key_filename = "/home/openkai/sc-admin.pem"

    pack_codes()

    args = get_args()
    if args.dev:
        APP_PATH = APP_PATH + '-dev'
        execute(deploy_app)
        execute(run_app_dev)
    elif args.test:
        APP_PATH = APP_PATH + '-test'
        execute(deploy_app)
        execute(run_app_test)
    else:
        execute(deploy_app)
        execute(run_app)

    del_packed_codes()
