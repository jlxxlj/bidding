# coding=utf-8
# author="JianghuaZhao"

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart, MIMEBase
from email.header import Header
import email.encoders
from scpy.logger import get_logger

logger = get_logger(__file__)


def send_warn_email(receivers, error_logger_name):
    sender = "socialcredicts@163.com"
    main_msg = MIMEMultipart()

    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    text_msg = MIMEText(u'具体错误信息请查看附件', 'plain', 'utf-8')
    main_msg.attach(text_msg)

    # 构造MIMEBase对象做为文件附件内容并附加到根容器
    contype = 'application/octet-stream'
    maintype, subtype = contype.split('/', 1)

    # 读入文件内容并格式化
    data = open(error_logger_name, 'rb')
    file_msg = MIMEBase(maintype, subtype)
    file_msg.set_payload(data.read())
    data.close()
    email.Encoders.encode_base64(file_msg)  # 把附件编码

    # 设置附件头
    basename = os.path.basename(error_logger_name)
    basename += ".txt"
    file_msg.add_header('Content-Disposition', 'attachment', filename=basename)  # 修改邮件头
    main_msg.attach(file_msg)

    # 设置根容器属性
    main_msg['From'] = sender
    main_msg['To'] = receivers
    main_msg['Subject'] = u'招投标监控爬虫内部错误，停止运行！'
    main_msg['Date'] = email.Utils.formatdate()

    try:
        server = smtplib.SMTP('smtp.163.com')
        server.login(user="socialcredicts@163.com", password="1socialcredits1")
        server.sendmail(sender, receivers, main_msg.as_string())
        logger.info(u"邮件发送成功")
    except smtplib.SMTPException, e:
        logger.error(u"无法发送邮件({0})".format(e.message))
    finally:
        server.close()


if __name__ == "__main__":
    send_warn_email("309927063@qq.com", "./py_log/errors-2016-08-29.log")
