# coding=utf-8
# author="Jianghua Zhao"

import sys
from scpy.logger import get_logger

from segment import paratokens
import classify
import re

reload(sys)
sys.setdefaultencoding("utf-8")

logger = get_logger(__file__)

reload(classify)

word_idx_map, f_pred_prob = classify.load_model()

re_company = re.compile(u"^[\u4e00-\u9fa5][\u4e00-\u9fa50-9a-zA-Z\(\)（）]+[\u4e00-\u9fa5]$")


def ner_of_html(html):
    html = u"<div>%s</div>" % html
    para_tokens = paratokens(html)
    tokens = []
    for i in range(len(para_tokens)):
        tokens += para_tokens[i]
    tokens = [token.strip() for token in tokens]
    tokens = [token for token in tokens if 4 <= len(token) <= 40]
    tokens = [token for token in tokens if re_company.search(token)]

    companies = list(set(
        [tokens[i] for i, x in enumerate(classify.company(tokens, word_idx_map, f_pred_prob))
         if x == 1]))

    return companies
