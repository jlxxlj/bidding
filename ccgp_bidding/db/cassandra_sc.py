#! /usr/bin/env python  
# -*- coding:utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import datetime
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from ..conf import config
from singleton import Singleton
from ..conf import CRAWLER_NAME

auth_provider = PlainTextAuthProvider(
    username=config.CAS_USERNAME, password=config.CAS_PASSWORD)


class CassandraUtil(object):
    """
    """
    __metaclass__ = Singleton

    def __init__(self, keyspace='crawler'):

        self.client = Cluster(
            contact_points=config.CAS_HOST,
            auth_provider=auth_provider
        )
        self.session = self.client.connect(keyspace)

    def _create_cql(self, data, table_name):
        cql = "INSERT INTO %s ({column_names}) VALUES ({values})" % table_name
        column_names = ''
        values = ''
        for item in table_name.items():
            column_names += item[0] + ','
            values += item[1] + ','
        column_names = column_names.strip(',')
        values = values.strip(',')
        cql = cql.format(column_names=column_names, values=values)
        return cql

    def insert(self, data, table_name):
        if not isinstance(data, data):
            raise Exception('insert data must be type of dict')

        if not isinstance(table_name, basestring):
            raise Exception('table name type error')
        self.session.execute(self._create_cql(data, table_name))
        self.log_data()

    def log_data(self, crawler_name=''):
        if not crawler_name:
            crawler_name = CRAWLER_NAME

        date = datetime.datetime.now().strftime('%Y-%m-%d')
        hour = datetime.datetime.now().hour
        self.session.execute("UPDATE crawler_log set count=count+1 WHERE date='%s' and hour=%d and crawler='%s'" % (
        date, hour, crawler_name))
