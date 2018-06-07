#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import copy
import tornado.web
import tornado.ioloop
from tornado.concurrent import run_on_executor
from tornado.web import HTTPError
from concurrent.futures import ThreadPoolExecutor

from scpy.threadlocal import set_threadlocal
from scpy.logger import get_logger

import uuid
from utils.pgutil import PgUtil
from db import postgresql_sc

logger = get_logger()

PG = PgUtil()
MAX_WORKERS = 512

database = postgresql_sc.PostgresqlUtil()
announce_keys = ["purchaser", "purchase_agent", "purchase_category", "title", "url", "region", "published_ts",
                 "announced_ts", "winning_ts", "announce_type", "amount", "unit", "currency"]
result_keys = ["winning_company", "winning_amount", "unit", "currency"]


class InfoHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    @run_on_executor
    def get(self):
        set_threadlocal('scid', str(uuid.uuid4()))
        logger.info('in tornado')
        try:
            result = "hello wold"
            self.write(result)
        except:
            logger.exception('info exception')
            raise HTTPError(500, 'info exception')

    @run_on_executor
    def post(self):
        announce_data = self.get_argument("announce_data")
        if announce_data is None:
            return

        announce_data = json.loads(announce_data)
        for key, value in announce_data.items():
            if key not in announce_keys + ["analysis_result"]:
                del announce_data[key]
            elif value is None or (isinstance(value, (str, unicode)) and len(value) == 0):
                del announce_data[key]

        analysis_result = announce_data.get("analysis_result")
        if analysis_result is None:
            return
        del announce_data["analysis_result"]

        winning_ts = announce_data.get("winning_ts")
        if winning_ts is None or winning_ts == "":
            announce_data["winning_ts"] = analysis_result["bid_time"]

        update_condition = {"url": announce_data.get("url")}
        database.update(table_name="bidding_announce", dict_data=announce_data, dict_condition=update_condition,
                        upsert=True)

        res = database.select(table_name="bidding_announce", dict_condition=update_condition)
        bidding_announce_id = res[0][0]
        delete_condition = {"bidding_announce_id": bidding_announce_id}
        database.delete(table_name="bidding_result", dict_condition=delete_condition)

        bid_result = analysis_result.get("bid_result")
        for i in range(len(bid_result)):
            result = bid_result[i]
            for key, value in result.items():
                if key not in result_keys:
                    del analysis_result[key]
                elif value is None or (isinstance(value, (str, unicode)) and len(value) == 0):
                    del result[key]
            bid_result[i] = result

        for com in bid_result:
            if com.get("winning_company") is None:
                continue
            com["bidding_announce_id"] = bidding_announce_id
            database.insert("bidding_result", com)

        logger.info("write an analysis result (%s)." % announce_data.get("url"))


class BiddingHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    @run_on_executor
    def get(self):
        self.set_header('Content-Type', 'application/json;charset="utf-8"')
        set_threadlocal('scid', str(uuid.uuid4()))
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
            and result.winning_company = '衡水海君密集柜业有限公司';
        '''
        try:
            data = PG.query_all_sql(query)
            result = {'result': data}
            self.write(result)
        except:
            logger.exception('info exception')
            raise HTTPError(500, 'info exception')


PORT = 9000
if __name__ == "__main__":
    application = tornado.web.Application(
        [
            (r"/info", InfoHandler),
            (r"/bidding", BiddingHandler)
        ])
    application.listen(PORT)
    logger.info('tornado server started on port %s', PORT)
    tornado.ioloop.IOLoop.instance().start()
