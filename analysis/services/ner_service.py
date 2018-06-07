# coding=utf-8
# author="Jianghua Zhao"
import os
import sys
import json
from bottle import run, request, post
from scpy.logger import get_logger
from scpy.xawesome_codechecker import timeit

PAR_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PAR_FOLDER not in sys.path:
    sys.path.append(PAR_FOLDER)

from scu_ner.ner import ner_of_html

reload(sys)
sys.setdefaultencoding("utf-8")

logger = get_logger(__file__)


@post('/ner')
@timeit(logger)
def ner_handler():
    # request_params = request.POST.decode('utf-8')
    data = request.json
    html = data.get("content", "")
    companies = ner_of_html(html)
    result = {"results": companies}
    return json.dumps(result)


if __name__ == '__main__':
    PORT = 16543
    logger.info('ner server started on port %s' % PORT)
    run(host='0.0.0.0', port=PORT, server='gunicorn', workers=2)
