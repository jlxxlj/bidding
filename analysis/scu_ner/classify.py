# -*- coding: utf-8 -*- 

import logging
# logger = logging.getLogger(__name__)
# logging.handlers = []

import os

current_folder, name = os.path.split(__file__)
import sys

sys.path.append(current_folder)

import cPickle as pkl

import jieba

import re

from bilstm_data_new import *

from bilstm_new import *


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        pass
        # import unicodedata
        # unicodedata.numeric(s)
        # return True
    except (TypeError, ValueError):
        pass

    return False


def load_model():
    model = current_folder + "/model_20160908/model_bilstm_v0.npz"
    # Model options
    model_options = locals().copy()

    x = pkl.load(open(current_folder + "/model_20160908/company_v0.model", "rb"))
    W, word_idx_map = x[0], x[1]

    with open(model + ".pkl", 'rb') as f:
        options = pkl.load(f)

    params = init_params(options, W)
    # load model parameters and set theano shared variables
    params = load_params(model, params)
    tparams = init_tparams(params)

    (use_noise, x, xr, mask, y, f_pred_prob, f_pred, cost) = build_model(tparams, options)

    return word_idx_map, f_pred_prob


# determine if the token is a company name
# return True / False
def company(tokens, word_idx_map, f_pred_prob):
    # TODO
    result = []
    data_x, data_y = [], []
    for line in tokens:
        seg_list = jieba.cut(line, cut_all=False)
        # seg_list = list(seg_list)
        seg_list = [token.strip().encode('utf-8') for token in seg_list if token.strip()]
        # print seg_list
        line = " ".join(seg_list)
        # line = str(line)
        # print '->', line
        sent = get_idx_from_sent(line, word_idx_map, 59)
        if len(sent) <= 1:
            sent = [0]
        # print sent
        data_x.append(sent)
        data_y.append(int(0))
    data = (data_x, data_y)
    # print len(data[0]), len(data[0])
    if not data[0]:
        return []
    iterator = get_minibatches_idx(len(data[0]), len(data[0]))
    probs = pred_probs(f_pred_prob, prepare_data, data, iterator)
    # print probs
    for prob in probs:
        if prob[0] > prob[1]:
            flag = True
        else:
            flag = False
        result.append(flag)
    return result


# determine if the token is an amount of money
# return True / False
def money(tokens):
    # TODO
    result = []
    # tokens = re.sub(' ','',tokens)
    # print tokens+'\n'+'-'*100
    seq = jieba.cut(tokens, cut_all=False)
    words = [s for s in seq if s != u' ']
    # print '/'.join(words)
    used = [False] * len(words)
    for ids in range(len(words)):
        if not used[ids]:
            if words[ids] in (u'元', u'万元', u'亿元', u'元整', u'万元整', u'亿元整') and (ids > 0):
                if not used[ids - 1] and is_number(words[ids - 1]):
                    result.append((words[ids - 1], words[ids]))
                    used[ids] = True
                    used[ids - 1] = True
            elif words[ids] in (u'$', u'￥', u'¥') and (ids < len(words) - 1):
                if is_number(words[ids + 1]):
                    # result.append(words[ids]+words[ids+1])
                    result.append((words[ids + 1], words[ids]))
                    used[ids] = True
                    used[ids + 1] = True
    """
    if len(result)!=0:
        print str(result)
    """

    return result
