# coding=utf-8
# author="Jianghua Zhao"

"""
爬虫监控进程
  通过监控logger来监控所有爬虫程序
"""

import os
import sys, getopt


def monitor(folder):
    files = os.listdir(folder)
    monitor_folders = []
    for name in files:
        if name.startswith("."):
            continue
        fld = os.path.join(folder, name, "py_log")
        if os.path.exists(fld):
            monitor_folders.append(fld)

    for fld in monitor_folders:
        print fld
    pass


def usage():
    print "Usage:"
    print "\tpython crawler_monitor.py [options]\n"
    print "Options: "
    print "\t-f, --folder=<folder>\tneed to monitor crawlers folder"
    print "\t-h, --help           \tshow script usage\n"


if __name__ == "__main__":
    argv = sys.argv
    opts, args = getopt.getopt(argv[1:], "hf:", ["folder=", "help"])

    folder, show_help = None, None
    for op, value in opts:
        if op == "-f" or op == "--folder":
            folder = value
        if op == "-h" or op == "--help":
            show_help = True

    if show_help or folder is None:
        usage()
    if folder:
        monitor(folder)
