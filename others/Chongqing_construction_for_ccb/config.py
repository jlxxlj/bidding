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

# postgreSQL config
POSTGRESQL_HOST = "sc-db.cfdjbes8ghlt.rds.cn-north-1.amazonaws.com.cn"
POSTGRESQL_PORT = '5432'
POSTGRESQL_USER_NAME = 'crawler'
POSTGRESQL_PASSWORD = '1qaz2wsx'
POSTGRESQL_DATABASE = 'crawler'

"""
公司画像服务地址
"""
COMPANY_PROFILE_URL = 'http://52.80.91.57:9030/company/profile/feature/batch'


"""
发送邮箱配置
"""
SMTP_HOST = "smtp.163.com"
EMAIL_SENDER = "socialcredicts@163.com"
EMAIL_PASSWORD = "1socialcredits1"


"""
others
"""
EMAIL_RECEIVERS = [
    "anya.chen@socialcredits.cn",
    "haiyang.jiang@socialcredits.cn",
    #"jianghua.zhao@socialcredits.cn",
    "shitong.sun@socialcredits.cn",
    "tao.xue@socialcredits.cn",
]
