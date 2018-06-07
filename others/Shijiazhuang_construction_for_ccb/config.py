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
if LOCAL_IP.startswith('10'):
    POSTGRESQL_HOST = '10.24.28.211'
else:
    POSTGRESQL_HOST = '114.55.28.251'
POSTGRESQL_PORT = '5432'
POSTGRESQL_USER_NAME = 'sc_crawler'
POSTGRESQL_PASSWORD = '1qaz2wsx'
POSTGRESQL_DATABASE = 'sc_crawler'

"""
公司画像服务地址
"""

if LOCAL_IP.startswith('10'):
    COMPANY_PROFILE_URL = 'http://10.132.3.22:9030/company/profile/feature/batch'
else:
    COMPANY_PROFILE_URL = 'http://192.168.31.116:9030/company/profile/feature/batch'

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
    "jianghua.zhao@socialcredits.cn",
]
