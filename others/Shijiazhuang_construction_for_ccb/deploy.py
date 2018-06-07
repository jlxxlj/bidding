# coding=utf-8
# author="Jianghua Zhao"

import os
from fabric.api import *

REMOTE_PATH = "/home/jianghua.zhao/sc-bidding/Shijiazhuang_construction_for_ccb"
tar_file_name = 'daily_work.tar.gz'
APP_PATH = REMOTE_PATH
APP_NAME = 'daily_work.py'


def tar_packages():
    delete_packages()
    with settings(warn_only=True):
        local('tar -zcf {name} *'.format(name=tar_file_name))


def delete_packages():
    if os.path.exists(tar_file_name):
        local('rm {name}'.format(name=tar_file_name))


@parallel(pool_size=50)
def get_file(rmt_path, lcl_path):
    with hide("running"):
        get(rmt_path, lcl_path)


@parallel(pool_size=50)
def deploy():
    with settings(warn_only=True):
        run('rm -r ' + REMOTE_PATH + '/*')

    run('mkdir -p ' + REMOTE_PATH)
    put(tar_file_name, REMOTE_PATH)

    with cd(REMOTE_PATH):
        run('tar -zxf {name}'.format(name=tar_file_name), shell='/bin/bash')
        run('rm {name}'.format(name=tar_file_name), shell='/bin/bash')


@parallel(pool_size=50)
def kill_all():
    with settings(warn_only=True):
        sudo('pkill -f %s' % APP_NAME)


@parallel(pool_size=50)
def deploy_run():
    with cd(REMOTE_PATH):
        run('$(nohup python %s 1>/dev/null  2>/dev/null &) && sleep 1' % APP_NAME)


if __name__ == '__main__':
    env.hosts = [
        'jianghua.zhao@192.168.31.157',
    ]
    env.password = 'zhao513975'

    execute(get_file, REMOTE_PATH + "/data/announce.db", "./data/announce.db")
    tar_packages()
    execute(deploy)
