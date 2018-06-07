# coding=utf-8
# author="Jianghua Zhao"

"""
部署爬虫
"""

import sys
import os

from fabric.api import env, execute, parallel, settings, run, put, cd, sudo, local

reload(sys)
sys.setdefaultencoding("utf-8")

REMOTE_PATH = "/home/jianghua.zhao/bid_crawlers/"
# REMOTE_PATH = "/home/jianghua.zhao/py_project/crawler/"
SRC_PATH = REMOTE_PATH + "crawler"
MNT_PATH = REMOTE_PATH + "monitors"
CTH_PATH = REMOTE_PATH + "cathe"
VRE_PATH = "/home/jianghua.zhao/py_project/crawler"

tar_file_name = "crawler.tar.gz"


def tar_packages():
    delete_packages()
    with settings(warn_only=True):
        local('tar -zcf {name} *'.format(name=tar_file_name))


def delete_packages():
    if os.path.exists(tar_file_name):
        local('rm {name}'.format(name=tar_file_name))


@parallel(pool_size=10)
def collect_monitor_cathe(scr, dst):
    with cd(SRC_PATH):
        cmd = "python cathe_manage.py --op=0 --src=%s --dst=%s" % (scr, dst)
        # run('$(%s) && sleep 1' % cmd)
        run('$(%s)' % cmd)


@parallel(pool_size=10)
def distribute_monitor_cathe(scr, dst):
    with cd(SRC_PATH):
        cmd = "python cathe_manage.py --op=1 --src=%s --dst=%s" % (scr, dst)
        # run('$(%s) && sleep 1' % cmd)
        run('$(%s)' % cmd)


@parallel(pool_size=10)
def stop_one_crawler(web_host):
    with settings(warn_only=True):
        sudo('pkill -f "filter_url=%s"' % web_host)


@parallel(pool_size=10)
def copy_source_code_to_crawler_folder(web_host):
    path = MNT_PATH + "/crawler" + "_" + web_host
    cathe_path = CTH_PATH + "/crawler" + "_" + web_host
    collect_monitor_cathe(path, cathe_path)
    with settings(warn_only=True):
        run('rm -rf ' + path + "*")
    run('cp -R ' + SRC_PATH + ' ' + path)
    distribute_monitor_cathe(cathe_path, path)


@parallel(pool_size=10)
def start_one_crawler(web_host):
    path = MNT_PATH + "/crawler" + "_" + web_host
    with cd(path):
        cmd = "python start_crawler.py --crawler_type=2 --filter_url=%s" % web_host
        cmd += " --apply_time_interval --time_st=2017-03-01"
        run("$(nohup {cmd} 1>/dev/null 2>&1 &) && sleep 1".format(cmd=cmd))


@parallel(pool_size=10)
def put_file():
    with settings(warn_only=True):
        run('rm -rf ' + SRC_PATH + "*")
        run("mkdir -p " + MNT_PATH)
        run("mkdir -p " + CTH_PATH)
    run("mkdir -p " + SRC_PATH)

    tar_packages()
    put(tar_file_name, SRC_PATH)
    with cd(SRC_PATH):
        run('tar -zxf {name}'.format(name=tar_file_name), shell='/bin/bash')
        run('rm {name}'.format(name=tar_file_name), shell='/bin/bash')
    delete_packages()


@parallel(pool_size=10)
def deploy(web_hosts):
    put_file()

    # collect_monitor_cathe(MNT_PATH, CTH_PATH)
    for web_host in web_hosts:
        stop_one_crawler(web_host)
        copy_source_code_to_crawler_folder(web_host)
    # distribute_monitor_cathe(CTH_PATH, MNT_PATH)

    for web_host in web_hosts:
        start_one_crawler(web_host)


@parallel(pool_size=10)
def deploy_all():
    import page_start
    import util

    hosts = set([])
    for start in page_start.start_urls:
        hosts.add(util.get_host_address(start[util.URL]))
    deploy(hosts)


@parallel(pool_size=10)
def deploy_chong_qing_crawlers():
    put_file()

    host = "chong-qing"
    cmd = "python start_crawler.py --crawler_type=2 --filter_region=%s --crawler_number=1" % "重庆"
    cmd += " --apply_time_interval --time_st=2017-05-01"
    with settings(warn_only=True):
        sudo('pkill -f python && sleep 5')

    copy_source_code_to_crawler_folder(host)

    path = MNT_PATH + "/crawler" + "_" + host
    with cd(path):
        run("source " + VRE_PATH + "/bin/activate && $(nohup {cmd} 1>/dev/null 2>&1 &) && sleep 1".format(cmd=cmd))


def deploy_chong_qing():
    env.hosts = [
        "jianghua.zhao@52.80.95.90"  # 重庆地区爬虫
    ]
    env.password = 'zhao513975'
    execute(deploy_chong_qing_crawlers)


@parallel(pool_size=10)
def deploy_he_bei_crawlers():
    put_file()

    host = "he-bei"
    cmd = "python start_crawler.py --crawler_type=2 --filter_region=%s --crawler_number=1" % "河北"
    cmd += " --apply_time_interval --time_st=2017-07-17"
    with settings(warn_only=True):
        sudo('pkill -f python && sleep 5')

    copy_source_code_to_crawler_folder(host)

    path = MNT_PATH + "/crawler" + "_" + host
    with cd(path):
        run("source " + VRE_PATH + "/bin/activate && $(nohup {cmd} 1>/dev/null 2>&1 &) && sleep 1".format(cmd=cmd))


def deploy_he_bei():
    env.hosts = [
        "jianghua.zhao@54.223.252.32"  # 河北地区爬虫
    ]
    env.password = 'zhao513975'
    execute(deploy_he_bei_crawlers)


def deploy_by_hosts():
    env.hosts = [
        "jianghua.zhao@192.168.31.157"  # 其余爬虫
    ]
    env.password = 'zhao513975'

    deploy_hosts = [
        "ggzy.jiangxi.gov.cn",
        "ggzyjy.jl.gov.cn",
        "www.bjztb.gov.cn",
        "www.ccgp-anhui.gov.cn",
        "www.ccgp-hainan.gov.cn",
        "www.ccgp-hunan.gov.cn",
        "www.ccgp-jiangsu.gov.cn",
        "www.ccgp-qinghai.gov.cn",
        "www.ccgp-shanxi.gov.cn",
        "www.ccgp.gov.cn",
        "www.chinabidding.org.cn",
        "www.gdgpo.gov.cn",
        "www.gszfcg.gansu.gov.cn",
        "www.gxgp.gov.cn",
        "www.gxzfcg.gov.cn",
        "www.gzzbw.cn",
        "www.hainan.gov.cn",
        "www.hbzbw.com",
        "www.hebggzy.cn",
        "www.hljcg.gov.cn",
        "www.lnzc.gov.cn",
        "www.nmgp.gov.cn",
        "www.nxzfcg.gov.cn",
        "www.sczfcg.com",
        "www.sdzbcg.com",
        "www.sxzhaobiao.com",
        "www.tjgp.gov.cn",
        "www.xzzbtb.gov.cn",
        "www.yjggzy.cn",
        "www.yngp.com",
        "www.zbs365.com",
        "www.zjzfcg.gov.cn",
        "zfcg.xjcz.gov.cn",
    ]

    execute(deploy, deploy_hosts)


if __name__ == "__main__":
    deploy_chong_qing()
    # deploy_he_bei()

    # deploy_by_hosts()
