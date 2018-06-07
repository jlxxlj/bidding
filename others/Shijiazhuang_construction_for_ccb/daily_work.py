# coding=utf-8
# author="Jianghua Zhao"

import json
import os
import sys
import datetime
import argparse

import psycopg2
import requests
from psycopg2.extras import RealDictCursor
import xlwt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart, MIMEBase
import email.encoders
from scpy.logger import get_logger

from config import *

folder_path = os.path.dirname(os.path.abspath(__file__))

reload(sys)
sys.setdefaultencoding("utf-8")

logger = get_logger(__file__)

RESOURCES = {}


def get_sqlite_connection():
    if "sqlite_conn" not in RESOURCES:
        import sqlite3
        db_path = os.path.join(folder_path, "data/announce.db")
        conn = sqlite3.connect(db_path, timeout=10.0)
        RESOURCES["sqlite"] = conn
    return RESOURCES["sqlite"]


def get_pg_connection():
    if "pg_conn" not in RESOURCES:
        import psycopg2
        conn = psycopg2.connect(database=POSTGRESQL_DATABASE, user=POSTGRESQL_USER_NAME, password=POSTGRESQL_PASSWORD,
                                host=POSTGRESQL_HOST, port=POSTGRESQL_PORT)
        RESOURCES["pg_conn"] = conn
    return RESOURCES["pg_conn"]


def sqlite_query_all(sql, parameters):
    conn = get_sqlite_connection()
    cur = conn.cursor()
    res = cur.execute(sql, parameters)
    res = res.fetchall()
    cur.close()
    return res


def pg_query_all(sql, parameters):
    conn = get_pg_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(sql, parameters)
    res = cur.fetchall()
    cur.close()
    return res


def select_announce_result_by_url(url):
    sql = """
        select
            announce.region as "region",
            to_char(announce.published_ts, 'YYYY-MM-DD') as "published_ts",
            result.winning_company as "winning_company",
            result.currency as "currency",
            result.winning_amount as "amount",
            result.unit as "unit",
            announce.project_name as "project_name",
            announce.title as "title",
            announce.purchaser as "purchaser_name",
            announce.purchaser_contact_phone as "purchaser_contact_phone",
            announce.purchase_agent as "agent_name",
            announce.agent_contact_phone as "agent_contact_phone",
            announce.url as "url",
            announce.unique_code as "unique_code"
        from bidding_announce announce, bidding_result result
        where announce.id=result.bidding_announce_id
        and announce.url=%s
        and result.role_type='winner';
    """
    return pg_query_all(sql, (url,))


def check_new_announce(announces, start_date, end_date):
    conn = get_sqlite_connection()
    cur = conn.cursor()

    check_exist_sql = "select * from announce where url=(?)"
    check_exist_before_date_sql = "select * from announce where url=(?) and end_ts<(?)"
    update_sql = "update announce set unique_code=(?) where url=(?)"
    check_repeat_before_date_sql = "select * from announce where unique_code=(?) and end_ts<(?)"
    insert_sql = "insert into announce(url, published_ts, unique_code, start_ts, end_ts) values (?,?,?,?,?)"

    result = []
    for announce in announces:
        url = announce.get("url")
        published_ts = announce.get("published_ts")
        unique_code = announce.get("unique_code")
        res = cur.execute(check_exist_before_date_sql, (url, start_date))
        if url and len(res.fetchall()) > 0:
            cur.execute(update_sql, (unique_code, url))
            continue
        res = cur.execute(check_repeat_before_date_sql, (unique_code, start_date))
        if unique_code and len(res.fetchall()) > 0:
            continue

        res = cur.execute(check_exist_sql, (url,))
        if len(res.fetchall()) <= 0:
            cur.execute(insert_sql, (url, published_ts, unique_code, start_date, end_date))

        result.append(announce)
    cur.close()
    conn.commit()
    return result


def set_style(name, height, bold=False):
    """
    设置单元格样式
    :param name:
    :param height:
    :param bold:
    :return:
    """
    style = xlwt.XFStyle()  # 初始化样式
    font = xlwt.Font()  # 为样式创建字体
    font.name = name  # 'Times New Roman'
    font.bold = bold
    font.color_index = 4
    font.height = height
    style.font = font
    return style


def write_excel(path, column_head, data):
    f = xlwt.Workbook(encoding="utf-8")
    sheet1 = f.add_sheet(sheetname=u"石家庄地区工程建设中标信息", cell_overwrite_ok=True)
    # 写入列名
    char_len = [len(column) for column in column_head]
    for i, column in enumerate(column_head):
        # sheet1.write(0, i, column, set_style('Times New Roman', 220, True))
        sheet1.write(0, i, column)
    # 写入内容
    for i, d in enumerate(data):
        for j, column in enumerate(column_head):
            # sheet1.write(i + 1, j, d.get(column, ""), set_style('Times New Roman', 220, False))
            dt = d.get(column, "")
            sheet1.write(i + 1, j, dt)
            if dt and len(str(dt)) > char_len[j]:
                char_len[j] = len(str(dt))
    # 设置列宽
    for i, cl in enumerate(char_len):
        sheet1.col(i).width = min(15000, max(3000, 180 * cl))
    f.save(path)


def export_shijiazhuang_construction(begin, end):
    # sql = """
    #     select
    #         announce.region as "region",
    #         to_char(announce.published_ts, 'YYYY-MM-DD') as "published_ts",
    #         result.winning_company as "winning_company",
    #         result.currency as "currency",
    #         result.winning_amount as "amount",
    #         result.unit as "unit",
    #         announce.project_name as "project_name",
    #         announce.title as "title",
    #         announce.purchaser as "purchaser_name",
    #         announce.purchaser_contact_phone as "purchaser_contact_phone",
    #         announce.purchase_agent as "agent_name",
    #         announce.agent_contact_phone as "agent_contact_phone",
    #         announce.url as "url"
    #     from bidding_announce announce, bidding_result result
    #     where announce.id=result.bidding_announce_id
    #     and announce.create_at>=%(begin_ts)s
    #     and announce.create_at<%(end_ts)s
    #     and result.role_type='winner'
    #     and announce.url like %(url_reg)s
    #     order by announce.published_ts desc, announce.url;
    # """

    sql = """
        select
            announce.region as "region",
            to_char(announce.published_ts, 'YYYY-MM-DD') as "published_ts",
            result.winning_company as "winning_company",
            result.currency as "currency",
            result.winning_amount as "amount",
            result.unit as "unit",
            announce.project_name as "project_name",
            announce.title as "title",
            announce.purchaser as "purchaser_name",
            announce.purchaser_contact_phone as "purchaser_contact_phone",
            announce.purchase_agent as "agent_name",
            announce.agent_contact_phone as "agent_contact_phone",
            announce.url as "url",
            announce.unique_code as "unique_code"
        from bidding_announce announce, bidding_result result
        where announce.id=result.bidding_announce_id
        and announce.city='石家庄市'
        and announce.project_type='工程建设'
        and announce.published_ts>=%(begin_ts)s
        and announce.published_ts<%(end_ts)s
        and announce.status<2
        and result.role_type='winner'
        order by announce.published_ts desc, announce.url;
    """

    # 将查询的结束日期加一天，保证能查到结束这一天的所有数据
    day_after_end = end + datetime.timedelta(days=1)

    args = {"begin_ts": begin, "end_ts": day_after_end, "url_reg": 'http://www.cqggzy.com/%'}
    conn = psycopg2.connect(database=POSTGRESQL_DATABASE, user=POSTGRESQL_USER_NAME, password=POSTGRESQL_PASSWORD,
                            host=POSTGRESQL_HOST, port=POSTGRESQL_PORT)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(sql, args)
    result = cur.fetchall()
    cur.close()
    return result


def cmp_datetime_str(x, y):
    from scpy.date_extractor import extract_first_date
    x = extract_first_date(x)
    y = extract_first_date(y)
    if x == y:
        return 0
    elif not x:
        return -1
    elif not y:
        return 1
    elif x < y:
        return -1
    elif x > y:
        return 1
    return 0


def fulfill_winner_info(data):
    winners = [d.get("winning_company", "") for d in data]

    max_tries = 30
    while max_tries > 0:
        try:
            res = requests.post(COMPANY_PROFILE_URL, data=json.dumps({
                'feaType': 'custom',
                'companyNameList': winners,
                'source': ['phone', "address"],
                'residentMapping': 'yes'}))
            if res.status_code == 200:
                break
            else:
                continue
        except requests.RequestException as e:
            logger.exception(e)
        finally:
            max_tries -= 1

    if res.status_code == 200:
        result = res.json().get("result", [])
        contacts, addresses = {}, {}
        for it in result:
            com = str(it.get("company", ""))
            if com not in contacts:
                contacts[com] = []
                addresses[com] = []
            contacts[com] += it.get("phone", [])
            addresses[com] += it.get("address", [])
        for d in data:
            # 联系电话
            phone = None
            for ph in contacts.get(d.get("winning_company"), []):
                if phone is None:
                    phone = ph
                elif "-" in ph:
                    phone = ph
                if "-" in ph:
                    break
            d["winner_contact_phone"] = phone
            # 地址
            addr = addresses.get(d.get("winning_company"), [])
            addr = sorted(addr, cmp=cmp_datetime_str, key=lambda x: x.get("time", ""), reverse=True)
            if len(addr) > 0:
                d["winner_address"] = addr[0].get("address")
            else:
                d["winner_address"] = None


def complete_bidding_project_name(data):
    for d in data:
        if not d.get("project_name"):
            d["project_name"] = d.get("title")


def fix_data(data):
    fulfill_winner_info(data)
    complete_bidding_project_name(data)


def send_email(receiver, subject, content, appendix):
    main_msg = MIMEMultipart()

    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    text_msg = MIMEText(content, 'plain', 'utf-8')
    main_msg.attach(text_msg)

    # 构造MIMEBase对象做为文件附件内容并附加到根容器
    contype = 'application/octet-stream'
    maintype, subtype = contype.split('/', 1)

    for file_path in appendix:
        file_path = os.path.abspath(file_path)
        # 读入文件内容并格式化
        with open(file_path, 'rb') as data_file:
            file_msg = MIMEBase(maintype, subtype)
            file_msg.set_payload(data_file.read())
            email.Encoders.encode_base64(file_msg)  # 把附件编码
        # 设置附件头
        basename = os.path.basename(file_path)
        file_msg.add_header('Content-Disposition', 'attachment', filename=str(basename))  # 修改邮件头
        main_msg.attach(file_msg)

    # 设置根容器属性
    main_msg['From'] = EMAIL_SENDER
    main_msg['To'] = receiver
    main_msg['Subject'] = subject
    main_msg['Date'] = email.Utils.formatdate()

    try:
        server = smtplib.SMTP(SMTP_HOST)
        server.login(user=EMAIL_SENDER, password=EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, receiver, main_msg.as_string())
        logger.info(u"邮件发送成功(receiver:%s)" % receiver)
    except smtplib.SMTPException, e:
        logger.error(u"无法发送邮件({0})".format(e.message))
    else:
        server.close()


def work_on_range(begin_date, end_date):
    column_head = ["region", "published_ts", "winning_company", "winner_contact_phone", "winner_address",
                   "currency", "amount", "unit", "project_name",
                   "purchaser_name", "purchaser_contact_phone",
                   "agent_name", "agent_contact_phone", "url",
                   ]

    data = export_shijiazhuang_construction(begin_date, end_date)

    fix_data(data)

    time_span_str = u"%s～%s" % (begin_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    path = u"data/石家庄%s工程建设项目中标结果.xls" % time_span_str
    path = os.path.join(folder_path, path)
    write_excel(path, column_head, data)

    for receiver in EMAIL_RECEIVERS:
        send_email(receiver,
                   subject=u"石家庄地区%s期间工程建设中标信息" % time_span_str,
                   content=u"%s 共有%s条中标信息。" % (time_span_str, len(data)),
                   appendix=[path, ])

    logger.info(u"%s 共有%s条中标信息。" % (time_span_str, len(data)))


def work_on_date(date):
    column_head = ["region", "published_ts", "winning_company", "winner_contact_phone", "winner_address",
                   "currency", "amount", "unit", "project_name",
                   "purchaser_name", "purchaser_contact_phone",
                   "agent_name", "agent_contact_phone", "url",
                   ]

    dt = sqlite_query_all("select * from announce where end_ts>=(?)", (date,))
    if len(dt) <= 0:
        pre_date = date + datetime.timedelta(days=-30)
        data = export_shijiazhuang_construction(pre_date, date)
        data = check_new_announce(data, date, date)
    else:
        dt = sqlite_query_all("select * from announce where start_ts>=(?) and end_ts<=(?)", (date, date))
        data = []
        for r in dt:
            url = r[1]
            data += select_announce_result_by_url(url)

    fix_data(data)

    time_str = date.strftime("%Y-%m-%d")
    path = u"data/石家庄%s工程建设项目中标结果.xls" % time_str
    path = os.path.join(folder_path, path)
    write_excel(path, column_head, data)

    for receiver in EMAIL_RECEIVERS:
        send_email(receiver,
                   subject=u"石家庄地区%s工程建设中标信息" % time_str,
                   content=u"%s 共有%s条中标信息。" % (time_str, len(data)),
                   appendix=[path, ])

    logger.info(u"%s 共有%s条中标信息。" % (time_str, len(data)))


def daily_work():
    today = datetime.datetime.now().date()
    today = datetime.datetime(year=today.year, month=today.month, day=today.day)
    yesterday = today + datetime.timedelta(days=-1)
    work_on_date(yesterday)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start", help="start date time: format (YYYYMMDD)")
    parser.add_argument("-e", "--end", help="end date time: format (YYYYMMDD)")
    args = parser.parse_args()
    if args.start:
        try:
            args.start = datetime.datetime.strptime(args.start, "%Y%m%d")
        except ValueError:
            print("Cannot format '%s' to a datetime." % args.start)
            sys.exit(1)
    if args.end:
        try:
            args.start = datetime.datetime.strptime(args.end, "%Y%m%d")
        except ValueError:
            print("Cannot format '%s' to a datetime." % args.end)
            sys.exit(1)
    return args


if __name__ == "__main__":
    options = get_args()
    if options.start and options.end:
        work_on_range(options.start, options.end)
    elif options.start:
        work_on_date(options.start)
    else:
        daily_work()
