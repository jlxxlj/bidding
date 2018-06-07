#! /usr/bin/env python  
# -*- coding:utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

"""
cassandra
"""
CAS_HOST = ['192.168.31.242']
CAS_USERNAME = 'cassandra'
CAS_PASSWORD = '15th January'

"""
KAFKA
"""
KAFKA_HOST = '192.168.31.114:9092'

"""
rabbitmqamqp
"""
AMQP_URL = 'amqp://sc-admin:1qaz2wsx@192.168.31.114:5672/%2F?heartbeat_interval=30'

"""
mongodb server IP address
"""
MONOG_HOST = '192.168.31.114'

"""10.24.28.211
online postgresql db connection information
"""
import socket

ip = socket.gethostbyname(socket.gethostname())
if ip.startswith('10'):
    POSTGRESQL_HOST = '10.24.28.211'
else:
    POSTGRESQL_HOST = '114.55.28.251'

POSTGRESQL_PORT = '5432'
POSTGRESQL_USER_NAME = 'sc_crawler'
POSTGRESQL_PASSWORD = '1qaz2wsx'
POSTGRESQL_DATABASE = 'sc_crawler'

"""
local service URL for update announce data and
its analysis result to online postgresql db
"""
if ip.startswith('10'):
    TORNADO_SERVICE_URL = "http://127.0.0.1:9000/info"
else:
    TORNADO_SERVICE_URL = "http://192.168.31.157:9000/info"

"""
EXTRACT_ENTITY_API URL
"""
if ip.startswith('10'):
    EXTRACT_ENTITY_API = 'http://10.161.237.234:29000/lp/api/lp?type=org'
else:
    EXTRACT_ENTITY_API = 'http://192.168.31.116:29000/lp/api/lp?type=org'

"""
source code save mode
"""
SOURCE_CODE_SAVE_MODE = 1
