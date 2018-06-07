#!/usr/bin/env python
# encoding=utf-8

import json
import sys
import datetime

import re
import tornado.web
from scpy.logger import get_logger
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.web import HTTPError

from service import dao
from service import bidding_service

import uuid
from datetime import datetime
from dateutil.relativedelta import relativedelta

reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = 'xlzd'

logger = get_logger(__file__)


class BiddingAsyncHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        self.set_header('Content-Type', 'application/json;charset="utf-8"')
        today = datetime.today()
        one_year_ago = datetime.today() + relativedelta(years=-1)
        company_name = self.get_argument('companyName', "", True)
        begin = self.get_argument('from', one_year_ago.strftime('%Y%m%d'), True)
        end = self.get_argument('to', today.strftime('%Y%m%d'), True)
        query = '''
            select distinct 
                   result.winning_company as "winningCompany",
                   result.winning_amount as "winningAmount",
                   result.unit as "unit",
                   result.currency as "currency",
                   announce.purchaser as "purchaser",
                   announce.purchase_agent as "purchaseAgent",
                   announce.purchase_category as "purchaseCategory",
                   announce.title as "title",
                   announce.url as "url",
                   announce.region as "region",
                   to_char(announce.published_ts, 'yyyy-mm-dd HH:MM:SS') as "publishedDateTime",
                   to_char(announce.announced_ts, 'yyyy-mm-dd') as "announcedDate",
                   to_char(announce.winning_ts, 'yyyy-mm-dd') as "winningDate",
                   announce.announce_type as "announceType",
                   announce.amount as "totalAmount",
                   announce.unit as "totalAmountUnit",
                   announce.currency as "totalAmountCurrency"
            from bidding_result result, bidding_announce announce
            where result.bidding_announce_id = announce.id
            and result.winning_company = %s
            and announce.published_ts::date >= %s
            and announce.published_ts::date <= %s
            order by to_char(announce.published_ts, 'yyyy-mm-dd HH:MM:SS') desc;
        '''
        data = dao.sc_crawler_query_all(query, (company_name, begin, end))
        if not data:
            raise HTTPError(404, 'not found')
        result = {'result': data}
        self.write(result)


class BiddingHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        self.set_header('Content-Type', 'application/json;charset="utf-8"')
        today = datetime.today()
        default_start_date = datetime(year=1900, month=1, day=1)
        company_name = self.get_argument('companyName', "", True)
        begin = self.get_argument('from', default_start_date.strftime('%Y%m%d'), True)
        end = self.get_argument('to', today.strftime('%Y%m%d'), True)

        # 参数验证
        if not company_name:
            raise HTTPError(400, "Not invalid company name")
        try:
            datetime.strptime(begin, "%Y%m%d")
            datetime.strptime(end, "%Y%m%d")
        except ValueError as e:
            raise HTTPError(400, "Not invalid time str")
        if begin > end:
            raise HTTPError(400, "From date should not be greater than to date")

        data = bidding_service.bidding_company_info_service(company_name, begin, end)

        if not data:
            raise HTTPError(404, 'not found')
        result = {'result': data}
        self.write(result)


# 将公司的历史名称数据进行融合
class MergedBiddingHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        self.set_header('Content-Type', 'application/json;charset="utf-8"')
        today = datetime.today()
        default_start_date = datetime(year=1900, month=1, day=1)
        company_name = self.get_argument('companyName', "", True)
        begin = self.get_argument('from', default_start_date.strftime('%Y%m%d'), True)
        end = self.get_argument('to', today.strftime('%Y%m%d'), True)

        # 参数验证
        if not company_name:
            raise HTTPError(400, "Not invalid company name")
        try:
            datetime.strptime(begin, "%Y%m%d")
            datetime.strptime(end, "%Y%m%d")
        except ValueError as e:
            raise HTTPError(400, "Not invalid time str")
        if begin > end:
            raise HTTPError(400, "From date should not be greater than to date")

        data = bidding_service.merged_bidding_company_info_service(company_name, begin, end)

        if not data:
            raise HTTPError(404, 'not found')
        result = {'result': data}
        self.write(result)


class BiddingContentSourceHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        self.set_header('Content-Type', 'application/json;charset="utf-8"')
        source_key = self.get_argument('sourceKey', "", True)
        announce_id = self.get_argument('announceID', "", True)
        if not source_key and not announce_id:
            raise HTTPError(400, 'need sourceKey or announceID')
        elif announce_id and not re.match(u"^\d+$", announce_id):
            raise HTTPError(400, 'need valid announceID')

        data = bidding_service.bidding_content_source_service(source_key, announce_id)

        if not data:
            raise HTTPError(404, 'not found')
        result = {'result': data}
        self.write(result)

    @gen.coroutine
    def post(self, *args, **kwargs):
        self.set_header('Content-Type', 'application/json;charset="utf-8"')
        source_key = self.get_argument('sourceKey', "", True)
        announce_id = self.get_argument('announceID', "", True)
        if not source_key and not announce_id:
            raise HTTPError(400, 'need sourceKey or announceID')
        elif announce_id and not re.match(u"^\d+$", announce_id):
            raise HTTPError(400, 'need valid announceID')

        data = bidding_service.bidding_content_source_service(source_key, announce_id)

        if not data:
            raise HTTPError(404, 'not found')
        result = {'result': data}
        self.write(result)


class BiddingInfoHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        self.set_header('Content-Type', 'application/json;charset="utf-8"')
        announce_id = self.get_argument('announceID', "", True)
        url = self.get_argument('url', "", True)
        if not announce_id and not url:
            raise HTTPError(400, 'no specified argument')
        elif announce_id and not re.match(u"^\d+$", announce_id):
            raise HTTPError(400, 'need valid announceID')

        data = bidding_service.bidding_info_service(announce_id, url)

        if not data:
            raise HTTPError(404, 'not found')
        result = {'result': data}
        self.write(result)


# ************************************** #
# 对各个地区的投标中标情况进行统计分析
# ************************************** #


PROJECT_TYPES = (u"政府采购", u"工程建设", u"矿产交易", u"产权交易", u"土地交易", u"农业开发", u"药品采购")


def get_arguments(handler):
    today = datetime.today()
    default_start_date = datetime(year=1900, month=1, day=1)

    # 约束参数
    begin = handler.get_argument('from', default_start_date.strftime('%Y%m%d'), True)
    end = handler.get_argument('to', today.strftime('%Y%m%d'), True)
    try:
        datetime.strptime(begin, "%Y%m%d")
        datetime.strptime(end, "%Y%m%d")
    except ValueError as e:
        raise HTTPError(400, "Not invalid time str")
    if begin > end:
        raise HTTPError(400, "From date should not be greater than to date")

    project_type = handler.get_argument('projectType', None, True)
    if project_type is not None:
        if re.match("^\d+$", project_type) and 0 <= int(project_type) < len(PROJECT_TYPES):
            project_type = PROJECT_TYPES[int(project_type)]
        else:
            raise HTTPError(400, "invalid argument projectType")

    arg_province = handler.get_argument('province', '', True)
    arg_city = handler.get_argument('city', '', True)
    if len(arg_province) > 0 and not re.search(u"^[\u4E00-\u9FA5]+$|^\d+$", arg_province):
        raise HTTPError(400, "invalid argument province")
    if len(arg_city) > 0 and not re.search(u"^[\u4E00-\u9FA5]+$|^\d+$", arg_city):
        raise HTTPError(400, "invalid argument city")
    province, city, county = bidding_service.get_region(arg_province, arg_city)
    if arg_province and not province:
        raise HTTPError(400, "invalid argument city")

    top_n = handler.get_argument('top', 10, True)
    if isinstance(top_n, (str, unicode)):
        if re.search(u"^\d+$", top_n):
            top_n = max(1, min(100, int(top_n)))
        else:
            raise HTTPError(400, "invalid argument top")

    page_size = handler.get_argument('pageSize', 10, True)
    if isinstance(page_size, (str, unicode)):
        if re.search(u"^\d+$", page_size):
            page_size = max(1, min(100, int(page_size)))
        else:
            raise HTTPError(400, "invalid argument page_size")

    page = handler.get_argument('page', 1, True)
    if isinstance(page, (str, unicode)):
        if re.search(u"^[1-9]\d*$", page):
            page = int(page)
        else:
            raise HTTPError(400, "invalid argument page")
    page -= 1

    return begin, end, project_type, province, city, county, top_n, page, page_size


class BiddingStatisticAmountCountRegionHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        self.set_header('Content-Type', 'application/json;charset="utf-8"')
        begin, end, project_type, province, city, county, top_n, page, page_size = get_arguments(self)
        result = bidding_service.bidding_statistic_service(op="amountCountRegion", begin=begin, end=end,
                                                           project_type=project_type, province=province,
                                                           top=top_n, city=city, county=county)

        if not result:
            raise HTTPError(404, "Not found")

        self.write({"result": result})


class BiddingStatisticAmountCountDateHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        self.set_header('Content-Type', 'application/json;charset="utf-8"')
        begin, end, project_type, province, city, county, top_n, page, page_size = get_arguments(self)
        result = bidding_service.bidding_statistic_service(op="amountCountDate", begin=begin, end=end,
                                                           project_type=project_type, province=province,
                                                           top=top_n, city=city, county=county)

        if not result:
            raise HTTPError(404, "Not found")

        self.write({"result": result})


class BiddingStatisticTopRoleHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        self.set_header('Content-Type', 'application/json;charset="utf-8"')
        begin, end, project_type, province, city, county, top_n, page, page_size = get_arguments(self)
        result = bidding_service.bidding_statistic_service(op="topRole", begin=begin, end=end,
                                                           project_type=project_type, province=province,
                                                           top=top_n, city=city, county=county)

        if not result:
            raise HTTPError(404, "Not found")

        self.write({"result": result})


class BiddingStatisticWinnerInfoHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        self.set_header('Content-Type', 'application/json;charset="utf-8"')
        begin, end, project_type, province, city, county, top_n, page, page_size = get_arguments(self)
        result = bidding_service.bidding_statistic_service(op="winnerInfo", begin=begin, end=end,
                                                           project_type=project_type, province=province,
                                                           city=city, county=county,
                                                           top=top_n, page=page, page_size=page_size)
        count = bidding_service.bidding_statistic_service(op="winnerInfoCount", begin=begin, end=end,
                                                          project_type=project_type, province=province,
                                                          city=city, county=county,
                                                          top=top_n, page=page, page_size=page_size)

        if not result:
            raise HTTPError(404, "Not found")

        self.write({"result": result, "totalCount": count})


class BiddingStatisticWinnerInfoCountHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        self.set_header('Content-Type', 'application/json;charset="utf-8"')
        begin, end, project_type, province, city, county, top_n, page, page_size = get_arguments(self)
        result = bidding_service.bidding_statistic_service(op="winnerInfoCount", begin=begin, end=end,
                                                           project_type=project_type, province=province,
                                                           city=city, county=county,
                                                           top=top_n, page=page, page_size=page_size)

        if not result:
            raise HTTPError(404, "Not found")

        self.write({"result": result})


# ************************************** #
# 对公司的投标中标情况进行统计分析
# ************************************** #

class BiddingStatisticByCompanyHandler(tornado.web.RequestHandler):
    """
    对公司的投标中标情况进行统计
    1、总投标次数
    2、总中标次数
    3、总投标金额
    4、总中标金额
    5、投标地域分布
    6、中标地域分布
    """

    @gen.coroutine
    def get(self):
        self.set_header('Content-Type', 'application/json;charset="utf-8"')
        # 获取参数
        company_name = self.get_argument("companyName", strip=True)

        today = datetime.today()
        default_start_date = datetime(year=1900, month=1, day=1)
        begin = self.get_argument("from", default_start_date.strftime("%Y%m%d"), True)
        end = self.get_argument("to", today.strftime("%Y%m%d"), True)

        # 参数验证
        if not company_name:
            raise HTTPError(400, "Not invalid company name")

        try:
            datetime.strptime(begin, "%Y%m%d")
            datetime.strptime(end, "%Y%m%d")
        except ValueError as e:
            raise HTTPError(400, "Not invalid time str")
        if begin > end:
            raise HTTPError(400, "From date should not be greater than to date")

        result = bidding_service.bidding_statistic_by_company_service(company_name=company_name,
                                                                      begin=begin,
                                                                      end=end)

        if not result:
            raise HTTPError(404, "Not found")

        self.write({"result": result})


class MergedBiddingStatisticByCompanyHandler(tornado.web.RequestHandler):
    """
    对公司的投标中标情况进行统计
    1、总投标次数
    2、总中标次数
    3、总投标金额
    4、总中标金额
    5、投标地域分布
    6、中标地域分布
    """

    @gen.coroutine
    def get(self):
        self.set_header('Content-Type', 'application/json;charset="utf-8"')
        # 获取参数
        company_name = self.get_argument("companyName", strip=True)

        today = datetime.today()
        default_start_date = datetime(year=1900, month=1, day=1)
        begin = self.get_argument("from", default_start_date.strftime("%Y%m%d"), True)
        end = self.get_argument("to", today.strftime("%Y%m%d"), True)

        # 参数验证
        if not company_name:
            raise HTTPError(400, "Not invalid company name")

        try:
            datetime.strptime(begin, "%Y%m%d")
            datetime.strptime(end, "%Y%m%d")
        except ValueError as e:
            raise HTTPError(400, "Not invalid time str")
        if begin > end:
            raise HTTPError(400, "From date should not be greater than to date")

        result = bidding_service.merged_bidding_statistic_by_company_service(company_name=company_name,
                                                                             begin=begin,
                                                                             end=end)

        if not result:
            raise HTTPError(404, "Not found")

        self.write({"result": result})


class BiddingStatisticByCompanyTrendHandler(tornado.web.RequestHandler):
    """
    对公司的投标中标情况的趋势进行统计
    1、总投标次数
    2、总中标次数
    3、总投标金额
    4、总中标金额
    5、投标地域分布
    6、中标地域分布
    """

    @gen.coroutine
    def get(self):
        self.set_header('Content-Type', 'application/json;charset="utf-8"')

        base_choice = {"month": 1, "quarter": 3, "halfYear": 6, "year": 12}

        # 获取参数
        company_name = self.get_argument("companyName", strip=True)
        base = self.get_argument("base", "month", strip=True)

        # 参数验证
        if not company_name:
            raise HTTPError(400, "Not invalid company name")
        if base not in base_choice:
            raise HTTPError(400, "Not invalid base")

        base = base_choice[base]
        result = bidding_service.bidding_statistic_by_company_trend_service(company_name=company_name, base=base)

        if not result:
            raise HTTPError(404, "Not found")

        self.write({"result": result})


class MergedBiddingStatisticByCompanyTrendHandler(tornado.web.RequestHandler):
    """
    对公司的投标中标情况的趋势进行统计
    1、总投标次数
    2、总中标次数
    3、总投标金额
    4、总中标金额
    5、投标地域分布
    6、中标地域分布
    """

    @gen.coroutine
    def get(self):
        self.set_header('Content-Type', 'application/json;charset="utf-8"')

        base_choice = {"month": 1, "quarter": 3, "halfYear": 6, "year": 12}

        # 获取参数
        company_name = self.get_argument("companyName", strip=True)
        base = self.get_argument("base", "month", strip=True)

        # 参数验证
        if not company_name:
            raise HTTPError(400, "Not invalid company name")
        if base not in base_choice:
            raise HTTPError(400, "Not invalid base")

        base = base_choice[base]
        result = bidding_service.merged_bidding_statistic_by_company_trend_service(company_name=company_name, base=base)

        if not result:
            raise HTTPError(404, "Not found")

        self.write({"result": result})
