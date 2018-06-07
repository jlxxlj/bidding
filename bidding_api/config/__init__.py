#!/usr/bin/env python
# encoding=utf-8

"""
配置：根据本地或者阿里云环境自动加载对应的配置。
外部直接通过 "import config" 或者 "from config import *" 即可。
"""

from xtls.codehelper import get_ip
if get_ip().startswith('192.168.'):
    from lcl_conf import *
else:
    from aws_conf import *
