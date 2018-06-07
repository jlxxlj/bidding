# coding=utf-8
# author="Jianghua Zhao"

import sys
import socket

reload(sys)
sys.setdefaultencoding('utf-8')

LOCAL_IP = socket.gethostbyname(socket.gethostname())

"""
DB configuration
"""
# cassandra
CAS_HOST = ['192.168.31.242']
CAS_USERNAME = 'cassandra'
CAS_PASSWORD = '15th January'

# KAFKA
KAFKA_HOST = '192.168.31.114:9092'

# mongodb server IP address
MONGO_HOST = '192.168.31.114'
MONGO_PORT = 27017
MONGO_DB_NAME = "bid_data"

# AWS config
AWS_ACCESS_KEY_ID = "AKIAPQSZXOZS5YSMKLIQ"
AWS_SECRET_ACCESS_KEY = "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"
AWS_REGION_NAME = "cn-north-1"

# postgreSQL config
if LOCAL_IP.startswith('10'):
    POSTGRESQL_HOST = '10.24.28.211'
else:
    POSTGRESQL_HOST = '114.55.28.251'
POSTGRESQL_PORT = '5432'
POSTGRESQL_USER_NAME = 'sc_crawler'
POSTGRESQL_PASSWORD = '1qaz2wsx'
POSTGRESQL_DATABASE = 'sc_crawler'

"""
rabbit mq amqp
"""
AMQP_URL = 'amqp://sc-admin:1qaz2wsx@192.168.31.114:5672/%2F?heartbeat_interval=30'
