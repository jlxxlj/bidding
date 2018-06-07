#! /usr/bin/env python
# -*- coding:utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from conf import config

from pymongo import MongoClient
from singleton import Singleton

class MongoUtil(object):
    __metaclass__ = Singleton

    def  __init__(self,):
        self.conn = MongoClient(config.MONOG_HOST)

    def get_connection(self):
        return self.conn

    def get_db(self, db_name):
        return self.conn[db_name]

    def get_coll(self, db_name, collection):
        return self.conn[db_name][collection]
