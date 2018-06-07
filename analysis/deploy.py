# coding=utf-8
# author="Jianghua Zhao"

import os
from fabric.api import *

REMOTE_PATH = "/home/jianghua.zhao/sc-bidding/analysis"
tar_file_name = 'analysis.tar.gz'
APP_PATH = REMOTE_PATH
APP_NAME = 'announce_analysis.py'


def tar_packages():
    if os.path.exists(tar_file_name):
        local('rm {name}'.format(name=tar_file_name))

    with settings(warn_only=True):
        local('tar -zcf {name} *'.format(name=tar_file_name))


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
def deploy_run(worker_num=3):
    for i in range(worker_num):
        path = REMOTE_PATH + "_" + str(i)
        run('cp -R ' + REMOTE_PATH + ' ' + path)
        with cd(path):
            run('$(nohup python %s 1>/dev/null  2>/dev/null &) && sleep 1' % APP_NAME)


if __name__ == '__main__':
    env.hosts = [
        "jianghua.zhao@54.223.176.191",
    ]
    env.password = "zhao513975"

    tar_packages()
    execute(deploy)
