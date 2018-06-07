# coding=utf-8
# author="Jianghua Zhao"

import sys, getopt
import os
import shutil


def is_cathe(folder):
    par_dir, name = os.path.split(folder)
    if name == "cathe":
        sub_names = os.listdir(folder)
        if "url_pool.pkl" in sub_names:
            return True
    return False


def get_all_cathe(folder):
    result = []
    if not os.path.exists(folder):
        return result
    names = os.listdir(folder)
    for name in names:
        path = os.path.join(folder, name)
        if os.path.isdir(path):
            if is_cathe(path):
                result.append(path)
            else:
                result += get_all_cathe(path)
    return result


def collect_cathe(src_folder, dst_folder):
    src_folder = os.path.abspath(src_folder)
    dst_folder = os.path.abspath(dst_folder)

    if os.path.exists(dst_folder):
        shutil.rmtree(dst_folder)
    cathe = get_all_cathe(src_folder)
    for item in cathe:
        new_item = item.replace(src_folder, dst_folder, 1)
        shutil.copytree(item, new_item)


def distribute_cathe(src_folder, dst_folder):
    src_folder = os.path.abspath(src_folder)
    dst_folder = os.path.abspath(dst_folder)

    cathe = get_all_cathe(src_folder)
    for item in cathe:
        new_item = item.replace(src_folder, dst_folder, 1)
        if os.path.exists(new_item):
            shutil.rmtree(new_item)
        shutil.copytree(item, new_item)


def usage():
    print "Usage:"
    print "\tpython cathe_manage.py [options]\n"
    print "Options:"
    print "\t--op=<operation>        \toperation name (0: 'collect_cathe' or 1: 'distribute_cathe')"
    print "\t--src=<src_folder>      \tsource folder of operation"
    print "\t--dst=<dst_folder>      \tdestination folder of operation"
    print "\t-h, --help              \tshow script usage"
    print ""


if __name__ == "__main__":
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "h", ["op=", "src=", "dst=", "help"])

    operation = None
    source_folder = None
    destine_folder = None

    for op, value in opts:
        if op == "--op":
            operation = int(value)
        if op == "--src":
            source_folder = value.rstrip("/")
        if op == "--dst":
            destine_folder = value.rstrip("/")
        if op == "-h" or op == "--help":
            usage()
    if len(argv) == 0:
        usage()
        exit(0)

    if operation is not None and source_folder and destine_folder:
        if operation == 0:
            collect_cathe(source_folder, destine_folder)
        else:
            distribute_cathe(source_folder, destine_folder)
    else:
        print "Please give complete arguments"
        usage()
