# coding=utf-8
# author="Jianghua Zhao"

import sys
import os

from bottle import run, request, post
from scpy.logger import get_logger
from scpy.xawesome_codechecker import timeit

PAR_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PAR_FOLDER not in sys.path:
    sys.path.append(PAR_FOLDER)

from announce_analysis_result_save import save_bidding_result

reload(sys)
sys.setdefaultencoding("utf-8")

logger = get_logger(__file__)


@post('/save')
@timeit(logger)
def save_bidding_result_handler():

    # request_params = request.POST.decode('utf-8')

    data = request.json
    announce_data = data.get("announceData", {})
    source = data.get("source", "")
    save_bidding_result(announce_data, source)


if __name__ == '__main__':
    PORT = 16542
    logger.info('ner server started on port %s' % PORT)
    run(host='0.0.0.0', port=PORT, server='gunicorn', workers=2)













