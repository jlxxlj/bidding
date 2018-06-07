# coding=utf-8
# author="Jianghua Zhao"

import singleton


class DBInterface(object):
    __metaclass__ = singleton.Singleton

    def __init__(self):
        pass

    # 插入
    def insert(self, table, data, **kwargs):
        raise NotImplementedError("insert method is not implemented")

    # 查找
    def select(self, table, condition, **kwargs):
        raise NotImplementedError("select method is not implemented")

    # 删除
    def delete(self, table, condition, **kwargs):
        raise NotImplementedError("delete method is not implemented")

    # 修改
    def update(self, table, condition, data, upsert, **kwargs):
        raise NotImplementedError("update method is not implemented")
