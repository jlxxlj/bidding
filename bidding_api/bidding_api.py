#!/usr/bin/env python
# encoding=utf-8

import tornado.web
from tornado.ioloop import IOLoop
import sys
from handler import *
import config

reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = 'xlzd'

logger = get_logger(__file__)

HANDLERS = [
    # (r'/api/bidding', BiddingAsyncHandler),
    (r'/api/bidding', BiddingHandler),
    (r'/api/bidding/merged', MergedBiddingHandler),
    (r'/api/bidding/source', BiddingContentSourceHandler),
    (r'/api/bidding/info', BiddingInfoHandler),
    (r'/api/bidding/test', BiddingHandler),
    (r'/api/bidding/test/source', BiddingContentSourceHandler),
    (r'/api/bidding/test/info', BiddingInfoHandler),
    (r'/api/bidding/statistic/amountCountRegion', BiddingStatisticAmountCountRegionHandler),
    (r'/api/bidding/statistic/amountCountDate', BiddingStatisticAmountCountDateHandler),
    (r'/api/bidding/statistic/topRole', BiddingStatisticTopRoleHandler),
    (r'/api/bidding/statistic/winnerInfo', BiddingStatisticWinnerInfoHandler),
    (r'/api/bidding/statistic/winnerInfoCount', BiddingStatisticWinnerInfoCountHandler),
    (r'/api/bidding/statistic/company', BiddingStatisticByCompanyHandler),
    (r'/api/bidding/statistic/company/merged', MergedBiddingStatisticByCompanyHandler),
    (r'/api/bidding/statistic/companyTrend', BiddingStatisticByCompanyTrendHandler),
    (r'/api/bidding/statistic/companyTrend/merged', MergedBiddingStatisticByCompanyTrendHandler),
]

if __name__ == '__main__':
    SERVER_PORT = 7000 if len(sys.argv) < 2 else int(sys.argv[1])

    app = tornado.web.Application(HANDLERS, debug=config.DEBUG)
    app.listen(SERVER_PORT, address='0.0.0.0')
    logger.info('tornado server started on port {port}'.format(port=SERVER_PORT))
    IOLoop.current().start()
