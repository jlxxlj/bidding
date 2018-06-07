# -*- coding: utf-8 -*-
# __author__ = 'Jianghua Zhao'
# jianghua.zhao@socialcredits.cn

import numpy as np
import datetime

import util
from result_template import *
from announce_attributes import *
from regulations import FIELD_REGS
from obtain_element_info import element_obtain_regular_func_table

import sys
import os

commonprefix = os.path.commonprefix

reload(sys)
sys.setdefaultencoding('utf-8')

REGULATE_ITEMS = True


def obtain_all_element_info(doc, src_html=None):
    table = element_obtain_regular_func_table()
    typs = [ELEM_TYPE_COMPANY_NAME, ELEM_TYPE_PERSON_NAME]

    element_info = []
    for k in range(len(doc)):
        info = {}
        for key, (obt_func, reg_func) in table.items():
            info[key] = [[], []]
            if key not in typs:
                strings, contexts = obt_func(doc[k], with_context=True)
                if REGULATE_ITEMS and reg_func:
                    for i in range(len(strings)):
                        strings[i] = reg_func(strings[i])
                info[key] = (strings, contexts)
        element_info.append(info)

    table_ = dict([(k, v) for k, v in table.items() if k in typs])
    for base_line in range(0, len(doc), 100):
        end_line = min(base_line + 100, len(doc))
        concat_doc = "\n".join(doc[base_line:end_line])
        # concat_info = {}
        for key, (obt_func, reg_func) in table_.items():
            if key == ELEM_TYPE_COMPANY_NAME:
                strings, contexts = obt_func(concat_doc, with_context=True, src_html=src_html)
            else:
                strings, contexts = obt_func(concat_doc, with_context=True)
            if REGULATE_ITEMS and reg_func:
                for i in range(len(strings)):
                    strings[i] = reg_func(strings[i])
            # concat_info[key] = (strings, contexts)

            for i in range(len(strings)):
                pref, suf = contexts[i]
                line_idx = base_line + pref.count("\n")
                idx = pref.rfind("\n")
                if idx >= 0:
                    pref = pref[idx + 1:]
                idx = suf.find("\n")
                if idx >= 0:
                    suf = suf[:idx]
                element_info[line_idx][key][0].append(strings[i])
                element_info[line_idx][key][1].append([pref, suf])

    return element_info


# ------------------------------------------------------------------- #
# **************** START 结合语义进行信息抽取方法 START **************** #

def evaluate_regulation(obj_strings, contexts, regulations):
    """
    根据规则提取信息
    :param obj_strings:目标字符串
    :param contexts:目标字符串的上下文
    :param regulations:规则约束[[Reg规则, 权重, 加权方式:加/乘]]
                       权重小于 1 大于 0 表示可能属于某一项，但具体属于哪一项未知
    :return: a list of tuple like (obj_string, priority), obj_string:目标字符串, priority:加权结果
    """
    res = []
    for i in range(len(obj_strings)):
        priority = 0
        for reg, wgt, way in regulations:
            if reg.evaluate(contexts[i][0], obj_strings[i], contexts[i][1]):
                if way == ADD_WEIGHT:
                    priority += wgt
                else:
                    priority *= wgt
        if priority > 0:
            res.append((obj_strings[i], priority))

    return res


def get_doc_info(doc, src_html=None):
    """
    依靠规则获取所有信息
    :param doc:
    :param src_html:
    :return:
    """
    doc_info = {}

    # 抽取所有元数据
    if len(doc) == 0:
        return doc_info
    element_info = obtain_all_element_info(doc, src_html=src_html)

    # 按规则分配元数据
    for i in range(len(doc)):
        item = element_info[i]
        for field_reg in FIELD_REGS:
            field_name = field_reg.get("field_name")
            elem_type = field_reg.get("elem_type")
            regulations = field_reg.get("regulations")
            info = item.get(elem_type)
            if field_name in (CANDIDATE_COMPANY_NAME, WINNING_COMPANY_NAME) and len(info) > 0 and len(info[0]) > 0:
                # 利用后缀规则过滤组织机构名称
                t_info = [[], []]
                for k, name in enumerate(info[0]):
                    if util.is_company_name(name):
                        t_info[0].append(info[0][k])
                        t_info[1].append(info[1][k])
                info = t_info
            if info:
                res = evaluate_regulation(info[0], info[1], regulations)
                if field_name not in doc_info:
                    doc_info[field_name] = []
                for j in range(len(res)):
                    doc_info[field_name].append((i, min(100, len(info[1][j][0])), res[j][0], res[j][1]))

    return doc_info


# **************** END 结合语义进行信息抽取方法 END **************** #
# --------------------------------------------------------------- #


# ----------------------------------------------------- #
# **************** START 组合信息 START **************** #

def find_best_match_info_item(doc_info, doc, attr, save_one=True):
    """
    找到每个项最大 priority 的匹配项
    组合公告信息,三个策略
       1、对于单个字段，如果有后选项的优先级>=1,则从中选出一个优先级最大的
       2、如果前面一行以内的范围有同一组的其他字段的候选项里有优先级>=1的， 则认为这一项的优先级也应当>=1
       3、同一个分段内，向上查找同一组的其他字段的候选项里有优先级>=1的， 则认为这一项的优先级也应当>=1
    :param doc_info:
    :param doc:
    :param attr:
    :param save_one:
    :return:
    """
    res = {}

    # 暂存所有组内的项
    t_doc_info = {}
    for key_ in attr:
        items_ = doc_info.get(key_)
        if isinstance(items_, list):
            if key_ not in t_doc_info:
                t_doc_info[key_] = []
            for it_ in items_:
                t_doc_info[key_].append(it_)
        else:
            t_doc_info[key_] = doc_info.get(key_)
    # 计算根据策略二传递的优先级
    for i in range(len(attr) - 1):
        for suf_key in attr:
            if not isinstance(t_doc_info[suf_key], list):
                continue
            for suf_it in t_doc_info[suf_key]:
                for pre_key in attr:
                    if pre_key == suf_key or not isinstance(t_doc_info[pre_key], list):
                        continue
                    for pre_it in t_doc_info[pre_key]:
                        if -1 <= pre_it[0] - suf_it[0] <= 0 and pre_it[3] >= 1:
                            if suf_it[3] < 1:
                                pos = t_doc_info[suf_key].index(suf_it)
                                suf_it = list(suf_it)
                                suf_it[3] += 1
                                t_doc_info[suf_key][pos] = tuple(suf_it)

    for key in attr:
        items = doc_info.get(key)
        if items:
            t = False  # 是否从该字段候选项内找到优先级>=1的项
            max_pro = max([it[3] for it in items])
            items = [it for it in items if it[3] == max_pro]
            if max_pro >= 1:
                if save_one:
                    res[key] = items[:1]
                else:
                    res[key] = items
                continue
            # 策略二
            items_ = t_doc_info.get(key)
            if items_:
                max_pro = max([it_[3] for it_ in items_])
                items_ = [it_ for it_ in items_ if it_[3] == max_pro]
                if max_pro >= 1:
                    if save_one:
                        res[key] = items_[:1]
                    else:
                        res[key] = items_
                    continue
            # 策略三
            # 没有找到，看属于同一段内，是否有同一目标的属性
            for it in items:
                line_idx, pos_idx, val, pro = it

                # 计算这一项所在段的起始位置
                seg_st = line_idx
                pref_len = doc[line_idx].rfind(">>") + 1
                for k in range(line_idx - 1, -1, -1):
                    com_prefix = commonprefix([doc[line_idx], doc[k]])
                    com_prefix = com_prefix[:(com_prefix.rfind(">>") + 1)]
                    if not (0 < pref_len <= len(com_prefix)):
                        seg_st = k + 1
                        break
                # 一组字段所确定的段的范围内，不应该包括明确属于其他组字段的项
                for key_ in doc_info.keys():
                    items_ = doc_info.get(key_)
                    if key_ in attr or not isinstance(items_, list):
                        continue
                    for it_ in items_:
                        line_idx_, pos_idx_, val_, pro_ = it_
                        if seg_st <= line_idx_ < line_idx and pro_ >= 1:
                            seg_st = line_idx_ + 1

                for key_ in attr:
                    items_ = doc_info.get(key_)
                    if key_ == key or not isinstance(items_, list):
                        continue
                    for it_ in items_:
                        line_idx_, pos_idx_, val_, pro_ = it_
                        if seg_st <= line_idx_ <= line_idx and pro_ >= 1:
                            if save_one is True:
                                res[key] = [(line_idx, pos_idx, val, pro + 1)]
                                t = True
                                break
                            else:
                                if key not in res:
                                    res[key] = []
                                res[key].append((line_idx, pos_idx, val, pro + 1))
                    if t:
                        break
                if t:
                    break

        if key not in res:
            res[key] = []
    return res


def delete_from_doc_info_items(doc_info, items, compare_dim=[0, 1, 2]):
    """
    从文档信息中删除 items
    :param doc_info:
    :param items:
    :param compare_dim:
    :return:
    """
    for key in doc_info.keys():
        val = doc_info[key]
        if not isinstance(val, list):
            continue
        for it_ in items:
            for it in doc_info[key]:
                comp_res = True
                for dim in compare_dim:
                    if it[dim] != it_[dim]:
                        comp_res = False
                        break
                if comp_res:
                    doc_info[key].remove(it)
                    break


def match(distance_matrix):
    """
    # 使用动态规划，搜索所以可能情况
    :param distance_matrix:
    :return:
    """
    is_transposed = False
    row_num, col_num = distance_matrix.shape
    if row_num > col_num:
        distance_matrix = distance_matrix.T
        row_num, col_num = col_num, row_num
        is_transposed = True

    cost_0 = np.ones_like(distance_matrix)  # 正向的损失值
    route_0 = np.zeros_like(distance_matrix, dtype=int)  # 正向的路径
    cost_1 = np.ones_like(distance_matrix)  # 反向的损失值
    route_1 = np.zeros_like(distance_matrix, dtype=int)  # 反向的路径
    # cost_0 = util.ones_matrix_like(distance_matrix)
    # route_0 = util.zeros_matrix_like(distance_matrix)
    # cost_1 = util.ones_matrix_like(distance_matrix)
    # route_1 = util.zeros_matrix_like(distance_matrix)

    space = col_num - row_num + 1  # 可以调整的空间

    for j in range(space):  # 初始化第一行的损失值
        if distance_matrix[0][j] > 0:
            c0 = abs(distance_matrix[0][j])
            c1 = abs(distance_matrix[0][j]) * 10000
        else:
            c0 = abs(distance_matrix[0][j]) * 10000
            c1 = abs(distance_matrix[0][j])
        cost_0[0][j] = c0
        cost_1[0][j] = c1

    for i in range(1, row_num):
        for j in range(i, i + space):
            if distance_matrix[i][j] > 0:
                c0 = abs(distance_matrix[i][j])
                c1 = abs(distance_matrix[i][j]) * 10000
            else:
                c0 = abs(distance_matrix[i][j]) * 10000
                c1 = abs(distance_matrix[i][j])
            t0, t1 = None, None
            for k in range(i - 1, j):
                if t0 is None or cost_0[i - 1][k] + c0 < t0:
                    t0 = cost_0[i - 1][k] + c0
                    route_0[i][j] = k
                if t1 is None or cost_1[i - 1][k] + c1 < t1:
                    t1 = cost_1[i - 1][k] + c1
                    route_1[i][j] = k
            cost_0[i][j] = t0
            cost_1[i][j] = t1

    t, route, dirct = None, None, None
    for k in range(row_num - 1, col_num):
        if t is None or cost_0[-1][k] < t:
            t = cost_0[-1][k]
            route, dirct = k, 0
        if t is None or cost_1[-1][k] < t:
            t = cost_1[-1][k]
            route, dirct = k, 1

    match_i = [route]
    for i in range(row_num - 1, 0, -1):
        if dirct == 0:
            match_i.append(route_0[i][match_i[-1]])
        else:
            match_i.append(route_1[i][match_i[-1]])
    match_i.reverse()

    origin_i = list(range(row_num))
    if is_transposed:
        origin_i, match_i = match_i, origin_i

    return dict(zip(origin_i, match_i))


def match_info(items_0, items_1):
    num_0 = len(items_0)
    num_1 = len(items_1)
    if num_0 == 0:
        return {}
    elif num_1 == 0:
        match_table = {}
        for i in range(num_0):
            match_table[i] = None
        return match_table
    dis_matrix = np.ones((num_0, num_1))
    # dis_matrix = util.ones_matrix((num_0, num_1))
    for i in range(num_0):
        for j in range(num_1):
            d0 = items_0[i][0] - items_1[j][0]
            d1 = items_0[i][1] - items_1[j][1]
            dis_matrix[i][j] = d0 + (1 if d0 >= 0 else -1) * 0.0001 * d1

    match_table = match(dis_matrix)

    return match_table


def assemble_announce_info(doc_info, doc):
    """
    组合公告信息,三个策略
       1、对于单个字段，如果有后选项的优先级>=1,则从中选出一个优先级最大的
       2、同一个分段内，向上查找同一组的其他字段的候选项里有优先级>=1的， 则认为这一项的优先级也应当>=1
       3、对于文档没有内部段的情况下，如果前面一行以内的范围有同一组的其他字段的候选项里有优先级>=1的， 则认为这一项的优先级也应当>=1
    :param doc_info:
    :param doc:
    :return:
    """
    announce_attr = [ANNOUNCED_TS, WINNING_TS, DEAL_TS, OPEN_BID_TS, EVALUATE_TS, END_BID_TS]

    result = {}
    for attr in announce_attr:
        res = find_best_match_info_item(doc_info=doc_info, doc=doc, attr=[attr])
        confirm_items = []
        for v in res.values():
            confirm_items += v
        delete_from_doc_info_items(doc_info, confirm_items)
        doc_info.update(res)
        result.update(res)

    for attr in result.keys():
        if len(result[attr]) > 0:
            result[attr] = result[attr][0][2]
        else:
            result[attr] = None

    return result


def assemble_project_info(doc_info, doc):
    """
    # 有共同的前缀 "项目"
    :param doc_info:
    :param doc:
    :return:
    """
    # 项目属性集合
    project_attr = [PROJECT_NAME, PROJECT_ID, PROJECT_CONTACT_NAME, PROJECT_CONTACT_PHONE, PROJECT_TYPE, PROJECT_BUDGET]

    result = find_best_match_info_item(doc_info, doc, project_attr)
    # 将已经确定的项从文档信息中删除
    confirm_items = []
    for v in result.values():
        confirm_items += v
    delete_from_doc_info_items(doc_info, confirm_items)
    doc_info.update(result)

    for attr in result.keys():
        if len(result[attr]) > 0:
            result[attr] = result[attr][0][2]
        else:
            result[attr] = None

    return result


def assemble_purchaser_info(doc_info, doc):
    """
    # 有共同的前缀 "采购"
    :param doc_info:
    :param doc:
    :return:
    """
    purchaser_attr = [PURCHASER_NAME, PURCHASER_ADDRESS, PURCHASER_CONTACT_NAME, PURCHASER_CONTACT_PHONE,
                      PURCHASE_CATEGORY, PURCHASE_TYPE]

    result = find_best_match_info_item(doc_info, doc, purchaser_attr)

    # 将确定的项从文档信息中删除
    confirm_items = []
    for v in result.values():
        confirm_items += v
    delete_from_doc_info_items(doc_info, confirm_items, compare_dim=[2])
    doc_info.update(result)

    for attr in result.keys():
        if len(result[attr]) > 0:
            result[attr] = result[attr][0][2]
        else:
            result[attr] = None

    return result


def assemble_agent_info(doc_info, doc):
    # 有共同的前缀 "代理"

    agent_attr = [AGENT_NAME, AGENT_ADDRESS, AGENT_CONTACT_NAME, AGENT_CONTACT_PHONE]

    result = find_best_match_info_item(doc_info, doc, agent_attr)

    # 将确定的项从文档信息中删除
    confirm_items = []
    for v in result.values():
        confirm_items += v
    delete_from_doc_info_items(doc_info, confirm_items, compare_dim=[2])
    doc_info.update(result)

    for attr in result.keys():
        if len(result[attr]) > 0:
            result[attr] = result[attr][0][2]
        else:
            result[attr] = None

    return result


def assemble_candidate_info(doc_info, doc):
    candidate_attr = [CANDIDATE_COMPANY_NAME, CANDIDATE_COMPANY_ADDRESS, CANDIDATE_MONEY, CANDIDATE_RANK]

    result = {SEGMENTS: []}

    # 筛选出候选公司
    cdt_cn = doc_info.get(CANDIDATE_COMPANY_NAME)
    if isinstance(cdt_cn, list) and len(cdt_cn) > 0:
        max_pro = max([it[3] for it in cdt_cn])
        cdt_cn = [it for it in cdt_cn if it[3] == max_pro]
        if max_pro < 1:
            cdt_cn = []
    # 筛选出候选公司排序
    cdt_rank = doc_info.get(CANDIDATE_RANK)
    if isinstance(cdt_rank, list) and len(cdt_rank) > 0:
        max_pro = max([it[3] for it in cdt_rank])
        cdt_rank = [it for it in cdt_rank if it[3] == max_pro]
        if max_pro < 1:
            cdt_rank = []
    # 匹配候选公司以及排序
    if len(cdt_cn) == 0:
        for attr in candidate_attr:
            doc_info[attr] = []
        return result
    elif len(cdt_rank) == 0:
        for attr in candidate_attr:
            doc_info[attr] = []
        return result
    elif len(cdt_cn) < len(cdt_rank):
        idx = [x[0] for x in cdt_cn]
        comm_pref = commonprefix([doc[x] for x in idx])
        comm_pref_lens = []
        for i in range(len(cdt_rank) - len(cdt_cn)):
            idx_ = [cdt_rank[x][0] for x in range(i, len(cdt_cn) + i)]
            comm_pref_ = commonprefix([doc[x] for x in idx_])
            pref = commonprefix([comm_pref, comm_pref_])
            comm_pref_lens.append(len(pref))
        max_pref_len, st, ed = 0, 0, len(comm_pref_lens)
        for i in range(len(comm_pref_lens)):
            if comm_pref_lens[i] > max_pref_len:
                st = i
                max_pref_len = comm_pref_lens[i]
            elif comm_pref_lens[i] < max_pref_len:
                ed = i
        cdt_rank = cdt_rank[st:len(cdt_cn) + ed]
    elif len(cdt_rank) < len(cdt_cn):
        idx = [x[0] for x in cdt_rank]
        comm_pref = commonprefix([doc[x] for x in idx])
        comm_pref_lens = []
        for i in range(len(cdt_cn) - len(cdt_rank)):
            idx_ = [cdt_cn[x][0] for x in range(i, len(cdt_rank) + i)]
            comm_pref_ = commonprefix([doc[x] for x in idx_])
            pref = commonprefix([comm_pref, comm_pref_])
            comm_pref_lens.append(len(pref))
        max_pref_len, st, ed = 0, 0, len(comm_pref_lens)
        for i in range(len(comm_pref_lens)):
            if comm_pref_lens[i] > max_pref_len:
                st = i
                max_pref_len = comm_pref_lens[i]
            elif comm_pref_lens[i] < max_pref_len:
                ed = i
        cdt_cn = cdt_cn[st:len(cdt_rank) + ed]

    res = [candidate_template() for k in range(len(cdt_cn))]
    for i in range(len(res)):
        res[i][CANDIDATE_COMPANY_NAME] = cdt_cn[i]
    match_table = match_info(cdt_cn, cdt_rank)
    for i, j in match_table.items():
        if j is not None:
            res[i][CANDIDATE_RANK] = cdt_rank[j]
        else:
            res[i][CANDIDATE_RANK] = None

    cdt_cn = [cdt_cn[x] for x in match_table.keys() if x is not None]
    cdt_rank = [cdt_rank[x] for x in match_table.values() if x is not None]
    # 从doc_info中删除已经确定的
    # 从doc_info中删除已经确定的
    # delete_from_doc_info_items(doc_info, cdt_cn)
    delete_from_doc_info_items(doc_info, cdt_rank)

    # 筛选投标金额和地址
    cdt_adr = doc_info.get(CANDIDATE_COMPANY_ADDRESS)
    if isinstance(cdt_adr, list) and len(cdt_adr) > 0:
        max_pro = max([it[3] for it in cdt_adr])
        cdt_adr = [it for it in cdt_adr if it[3] == max_pro]
        if max_pro >= 1:
            delete_from_doc_info_items(doc_info, cdt_adr)
        else:
            idx = [x[0] for x in cdt_cn]
            idx += [x[0] for x in cdt_rank]
            comm_pref = commonprefix([doc[x] for x in idx])
            comm_pref = comm_pref[:(comm_pref.rfind(">>") + 1)]
            t = []
            for i in range(len(cdt_adr)):
                comm_pref_ = commonprefix([comm_pref, doc[cdt_adr[i][0]]])
                if len(comm_pref) == len(comm_pref_) > 0:
                    t.append(cdt_adr[i])
            cdt_adr = t
    cdt_mn = doc_info.get(CANDIDATE_MONEY)
    if isinstance(cdt_mn, list) and len(cdt_mn) > 0:
        max_pro = max([it[3] for it in cdt_mn])
        cdt_mn = [it for it in cdt_mn if it[3] == max_pro]
        if max_pro >= 1:
            delete_from_doc_info_items(doc_info, cdt_mn)
        else:
            idx = [x[0] for x in cdt_cn]
            idx += [x[0] for x in cdt_rank]
            comm_pref = commonprefix([doc[x] for x in idx])
            comm_pref = comm_pref[:(comm_pref.rfind(">>") + 1)]
            t = []
            for i in range(len(cdt_mn)):
                comm_pref_ = commonprefix([comm_pref, doc[cdt_mn[i][0]]])
                if len(comm_pref) == len(comm_pref_) > 0:
                    t.append(cdt_mn[i])
            cdt_mn = t

    match_table = match_info(cdt_cn, cdt_adr)
    for i, j in match_table.items():
        if j is not None:
            res[i][CANDIDATE_COMPANY_ADDRESS] = cdt_adr[j]
        else:
            res[i][CANDIDATE_COMPANY_ADDRESS] = None
    match_table = match_info(cdt_cn, cdt_mn)
    for i, j in match_table.items():
        if j is not None:
            res[i][CANDIDATE_MONEY] = cdt_mn[j]
        else:
            res[i][CANDIDATE_MONEY] = None

    # 查找最近的角色名
    role_names = doc_info.get(ROLE_NAME)
    for i in range(len(res)):
        line_idx = res[i][CANDIDATE_COMPANY_NAME][0]
        for name in role_names:
            if name[0] == line_idx:
                res[i][ROLE_NAME] = name
                break

    # 候选公司分包
    rank_set = []
    candidates = []
    for cand in res:
        rank = cand.get(CANDIDATE_RANK)
        if rank is not None:
            if rank in rank_set:
                rank_set = []
                seg = segment_template()
                seg[CANDIDATES] = candidates
                result[SEGMENTS].append(seg)
            rank_set.append(rank[2])
            candidates.append(cand)
    if len(candidates) > 0:
        seg = segment_template()
        seg[CANDIDATES] = candidates
        result[SEGMENTS].append(seg)

    return result


def match_company_money(com, mon, best_match):
    # 根据最佳的公司名和金额匹配结果来组合
    groups = {}
    for cm in com:
        group_key = "DEFAULT"
        for key, values in best_match.items():
            field_value = values["field_1"]
            if cm[:3] in field_value:
                group_key = key
                break
        if group_key not in groups:
            groups[group_key] = {"field_1": [], "field_2": []}
        groups[group_key]["field_1"].append(cm)

    for mn in mon:
        group_key = "DEFAULT"
        for key, values in best_match.items():
            field_value = values["field_2"]
            if mn[:3] in field_value:
                group_key = key
                break
        if group_key not in groups:
            continue
        groups[group_key]["field_2"].append(mn)

    matched_com_mon = {}
    for _, group in groups.items():
        com = group["field_1"]
        mon = group["field_2"]
        mat = match_info(com, mon)
        for i, j in mat.items():
            if i is not None and j is not None:
                matched_com_mon[com[i]] = mon[j]

    return matched_com_mon


def assemble_candidate_info_new(doc_info, doc):
    candidate_attr = [CANDIDATE_COMPANY_NAME, CANDIDATE_COMPANY_ADDRESS, CANDIDATE_MONEY, CANDIDATE_RANK]

    result = {SEGMENTS: []}

    # 筛选出候选公司
    cdt_cn = doc_info.get(CANDIDATE_COMPANY_NAME)
    if isinstance(cdt_cn, list) and len(cdt_cn) > 0:
        max_pro = max([it[3] for it in cdt_cn])
        cdt_cn = [it for it in cdt_cn if it[3] == max_pro]
        if max_pro < 1:
            cdt_cn = []
    # 筛选出候选公司排序
    cdt_rank = doc_info.get(CANDIDATE_RANK)
    if isinstance(cdt_rank, list) and len(cdt_rank) > 0:
        max_pro = max([it[3] for it in cdt_rank])
        cdt_rank = [it for it in cdt_rank if it[3] == max_pro]
        if max_pro < 1:
            cdt_rank = []
    # 匹配候选公司以及排序
    if len(cdt_cn) == 0:
        for attr in candidate_attr:
            doc_info[attr] = []
        return result, []
    # elif len(cdt_rank) == 0:
    #     for attr in candidate_attr:
    #         doc_info[attr] = []
    #     return result, []
    elif len(cdt_cn) < len(cdt_rank):
        idx = [x[0] for x in cdt_cn]
        comm_pref = commonprefix([doc[x] for x in idx])
        comm_pref_lens = []
        for i in range(len(cdt_rank) - len(cdt_cn)):
            idx_ = [cdt_rank[x][0] for x in range(i, len(cdt_cn) + i)]
            comm_pref_ = commonprefix([doc[x] for x in idx_])
            pref = commonprefix([comm_pref, comm_pref_])
            comm_pref_lens.append(len(pref))
        max_pref_len, st, ed = 0, 0, len(comm_pref_lens)
        for i in range(len(comm_pref_lens)):
            if comm_pref_lens[i] > max_pref_len:
                st = i
                max_pref_len = comm_pref_lens[i]
            elif comm_pref_lens[i] < max_pref_len:
                ed = i
        cdt_rank = cdt_rank[st:len(cdt_cn) + ed]
    # elif len(cdt_rank) < len(cdt_cn):
    #     idx = [x[0] for x in cdt_rank]
    #     comm_pref = commonprefix([doc[x] for x in idx])
    #     comm_pref_lens = []
    #     for i in range(len(cdt_cn) - len(cdt_rank)):
    #         idx_ = [cdt_cn[x][0] for x in range(i, len(cdt_rank) + i)]
    #         comm_pref_ = commonprefix([doc[x] for x in idx_])
    #         pref = commonprefix([comm_pref, comm_pref_])
    #         comm_pref_lens.append(len(pref))
    #     max_pref_len, st, ed = 0, 0, len(comm_pref_lens)
    #     for i in range(len(comm_pref_lens)):
    #         if comm_pref_lens[i] > max_pref_len:
    #             st = i
    #             max_pref_len = comm_pref_lens[i]
    #         elif comm_pref_lens[i] < max_pref_len:
    #             ed = i
    #     cdt_cn = cdt_cn[st:len(cdt_rank) + ed]

    res = [candidate_template() for k in range(len(cdt_cn))]
    for i in range(len(res)):
        res[i][CANDIDATE_COMPANY_NAME] = cdt_cn[i]
    match_table = match_info(cdt_cn, cdt_rank)
    for i, j in match_table.items():
        if j is not None:
            res[i][CANDIDATE_RANK] = cdt_rank[j]
        else:
            res[i][CANDIDATE_RANK] = None

    cdt_cn = [cdt_cn[x] for x in match_table.keys() if x is not None]
    cdt_rank = [cdt_rank[x] for x in match_table.values() if x is not None]
    # 从doc_info中删除已经确定的
    # 从doc_info中删除已经确定的
    # delete_from_doc_info_items(doc_info, cdt_cn)
    delete_from_doc_info_items(doc_info, cdt_rank)

    # 筛选投标金额和地址
    cdt_adr = doc_info.get(CANDIDATE_COMPANY_ADDRESS)
    if isinstance(cdt_adr, list) and len(cdt_adr) > 0:
        max_pro = max([it[3] for it in cdt_adr])
        cdt_adr = [it for it in cdt_adr if it[3] == max_pro]
        if max_pro >= 1:
            delete_from_doc_info_items(doc_info, cdt_adr)
        else:
            idx = [x[0] for x in cdt_cn]
            idx += [x[0] for x in cdt_rank]
            comm_pref = commonprefix([doc[x] for x in idx])
            comm_pref = comm_pref[:(comm_pref.rfind(">>") + 1)]
            t = []
            for i in range(len(cdt_adr)):
                comm_pref_ = commonprefix([comm_pref, doc[cdt_adr[i][0]]])
                if len(comm_pref) == len(comm_pref_) > 0:
                    t.append(cdt_adr[i])
            cdt_adr = t

    cdt_mn = doc_info.get(CANDIDATE_MONEY)
    if isinstance(cdt_mn, list) and len(cdt_mn) > 0:
        max_pro = max([it[3] for it in cdt_mn])
        cdt_mn = [it for it in cdt_mn if it[3] == max_pro]
        if max_pro >= 1:
            delete_from_doc_info_items(doc_info, cdt_mn)
        else:
            idx = [x[0] for x in cdt_cn]
            idx += [x[0] for x in cdt_rank]
            comm_pref = commonprefix([doc[x] for x in idx])
            comm_pref = comm_pref[:(comm_pref.rfind(">>") + 1)]
            t = []
            for i in range(len(cdt_mn)):
                comm_pref_ = commonprefix([comm_pref, doc[cdt_mn[i][0]]])
                if len(comm_pref) == len(comm_pref_) > 0:
                    t.append(cdt_mn[i])
            cdt_mn = t

    match_table = match_info(cdt_cn, cdt_adr)
    for i, j in match_table.items():
        if j is not None:
            res[i][CANDIDATE_COMPANY_ADDRESS] = cdt_adr[j]
        else:
            res[i][CANDIDATE_COMPANY_ADDRESS] = None
    #
    # # 根据最佳的公司名和金额匹配结果来组合
    # matched_company_money = match_company_money(cdt_cn, cdt_mn, best_match_company_money)
    # for i in range(len(res)):
    #     res[i][CANDIDATE_MONEY] = matched_company_money.get(res[i][CANDIDATE_COMPANY_NAME])

    # 查找最近的角色名
    role_names = doc_info.get(ROLE_NAME)
    for i in range(len(res)):
        line_idx = res[i][CANDIDATE_COMPANY_NAME][0]
        line_pos = doc[line_idx].find(res[i][CANDIDATE_COMPANY_NAME][2])
        dis = None
        for name in role_names:
            if name[0] == line_idx:
                pos = doc[line_idx].find(name[2])
                if dis is None or abs(line_pos - pos) < dis:
                    res[i][ROLE_NAME] = name
                    dis = abs(line_pos - pos)

    # 候选公司分包
    rank_set, candidates = [], []
    for cand in res:
        rank = cand.get(CANDIDATE_RANK)
        if rank is not None:
            if rank[2] in rank_set:
                seg = segment_template()
                seg[CANDIDATES] = candidates
                result[SEGMENTS].append(seg)
                rank_set, candidates = [], []
            rank_set.append(rank[2])
            candidates.append(cand)
        elif len(cdt_rank) == 0:
            candidates.append(cand)
    if len(candidates) > 0:
        seg = segment_template()
        seg[CANDIDATES] = candidates
        result[SEGMENTS].append(seg)

    return result, cdt_mn


def assemble_winner_info(doc_info, doc):
    """
    将中标信息进行组合
    :param doc_info:
    :param doc:
    :return:
    """
    wcn = doc_info.get(WINNING_COMPANY_NAME)
    if isinstance(wcn, list) and len(wcn) > 0:
        max_pro = max([it[3] for it in wcn])
        wcn = [it for it in wcn if it[3] == max_pro]
        if max_pro >= 1:
            delete_from_doc_info_items(doc_info, wcn)
    wad = doc_info.get(WINNING_COMPANY_ADDRESS)
    wmn = doc_info.get(WINNING_MONEY)

    result = {SEGMENTS: []}

    for i in range(len(wcn)):
        seg = segment_template()
        result[SEGMENTS].append(seg)
        winner = winner_template()
        winner[WINNING_COMPANY_NAME] = wcn[i]
        result[SEGMENTS][i][WINNER] = winner

    match_table = match_info(wcn, wad)
    for i, j in match_table.items():
        if j is not None:
            result[SEGMENTS][i][WINNER][WINNING_COMPANY_ADDRESS] = wad[j]
        else:
            result[SEGMENTS][i][WINNER][WINNING_COMPANY_ADDRESS] = None

    match_table = match_info(wcn, wmn)
    for i, j in match_table.items():
        if j is not None:
            result[SEGMENTS][i][WINNER][WINNING_MONEY] = wmn[j]
        else:
            result[SEGMENTS][i][WINNER][WINNING_MONEY] = None

    # 查找最近的角色名
    role_names = [name for name in doc_info.get(ROLE_NAME) if u"候选" not in name[2] and u"侯选" not in name[2]]
    for i in range(len(result[SEGMENTS])):
        line_idx = result[SEGMENTS][i][WINNER][WINNING_COMPANY_NAME][0]
        for name in role_names:
            if name[0] == line_idx:
                result[SEGMENTS][i][WINNER][ROLE_NAME] = name
                break

    return result


def assemble_winner_info_new(doc_info, doc):
    """
    将中标信息进行组合
    :param doc_info:
    :param doc:
    :return:
    """
    wcn = doc_info.get(WINNING_COMPANY_NAME)
    if isinstance(wcn, list) and len(wcn) > 0:
        max_pro = max([it[3] for it in wcn])
        wcn = [it for it in wcn if it[3] == max_pro]
        if max_pro >= 1:
            delete_from_doc_info_items(doc_info, wcn)

    wad = doc_info.get(WINNING_COMPANY_ADDRESS)
    if isinstance(wad, list) and len(wad) > 0:
        max_pro = max([it[3] for it in wad])
        max_pro = max_pro if max_pro < 1 else 1
        wad = [it for it in wad if it[3] >= max_pro]

    wmn = doc_info.get(WINNING_MONEY)
    if isinstance(wmn, list) and len(wmn) > 0:
        max_pro = max([it[3] for it in wmn])
        max_pro = max_pro if max_pro < 1 else 1
        wmn = [it for it in wmn if it[3] >= max_pro]

    result = {SEGMENTS: []}

    for i in range(len(wcn)):
        seg = segment_template()
        result[SEGMENTS].append(seg)
        winner = winner_template()
        winner[WINNING_COMPANY_NAME] = wcn[i]
        result[SEGMENTS][i][WINNER] = winner

    match_table = match_info(wcn, wad)
    for i, j in match_table.items():
        if j is not None:
            result[SEGMENTS][i][WINNER][WINNING_COMPANY_ADDRESS] = wad[j]
        else:
            result[SEGMENTS][i][WINNER][WINNING_COMPANY_ADDRESS] = None

    # # 根据最佳的公司名和金额匹配结果来组合
    # matched_company_money = match_company_money(wcn, wmn, best_match_company_money)
    # for i in range(len(result[SEGMENTS])):
    #     t = result[SEGMENTS][i][WINNER]
    #     result[SEGMENTS][i][WINNER][WINNING_MONEY] = matched_company_money.get(t[WINNING_COMPANY_NAME])

    # 查找最近的角色名
    role_names = [name for name in doc_info.get(ROLE_NAME) if u"候选" not in name[2] and u"侯选" not in name[2]]
    for i in range(len(result[SEGMENTS])):
        line_idx = result[SEGMENTS][i][WINNER][WINNING_COMPANY_NAME][0]
        line_pos = doc[line_idx].find(result[SEGMENTS][i][WINNER][WINNING_COMPANY_NAME][2])
        dis = None
        for name in role_names:
            if name[0] == line_idx:
                pos = doc[line_idx].find(name[2])
                if dis is None or abs(line_pos - pos) < dis:
                    result[SEGMENTS][i][WINNER][ROLE_NAME] = name
                    dis = abs(line_pos - pos)

    return result, wmn


def assemble_bidding_result_info(doc_info, doc):
    """
    组合中标信息
    :param doc_info:
    :param doc:
    :return:
    """
    bidding_result = {}

    # 找到总中标金额
    total_wmn = doc_info.get(TOTAl_WINNING_MONEY)
    if isinstance(total_wmn, list) and len(total_wmn) > 0:
        max_pro = max([it[3] for it in total_wmn])
        total_wmn = [it for it in total_wmn if it[3] == max_pro]
        if max_pro >= 1:
            bidding_result[TOTAl_WINNING_MONEY] = total_wmn[0][2]
            delete_from_doc_info_items(doc_info, total_wmn)
        else:
            bidding_result[TOTAl_WINNING_MONEY] = None

    # 找到专家名表
    expert_names = doc_info.get(EXPERT_NAMES)
    if isinstance(expert_names, list) and len(expert_names) > 0:
        max_pro = max([it[3] for it in expert_names])
        expert_names = [it for it in expert_names if it[3] == max_pro]
        if max_pro >= 1:
            bidding_result[EXPERT_NAMES] = ",".join([x[2] for x in expert_names])
            delete_from_doc_info_items(doc_info, expert_names, compare_dim=[2])
        else:
            bidding_result[EXPERT_NAMES] = None

    cand_result = assemble_candidate_info(doc_info, doc)
    bidding_result.update(cand_result)

    # 从可能中标公司中删除所有不是候选公司的公司名
    if len(cand_result[SEGMENTS]) > 0 and len(cand_result[SEGMENTS][0][CANDIDATES]) > 0:
        cand = []
        for seg in cand_result[SEGMENTS]:
            cand += seg[CANDIDATES]
        wcn = [x for x in doc_info[WINNING_COMPANY_NAME]]
        for cn in wcn:
            t = False
            for it in cand:
                ccn = it[CANDIDATE_COMPANY_NAME]
                if ccn[2] == cn[2]:
                    t = True
            if t is False:
                doc_info[WINNING_COMPANY_NAME].remove(cn)

    win_result = assemble_winner_info(doc_info, doc)

    # 将中标公司分段
    if len(win_result[SEGMENTS]) > 0:
        bias, i = 0, 0
        while i < len(win_result[SEGMENTS]):
            wcn = win_result[SEGMENTS][i][WINNER]
            if i + bias < len(bidding_result[SEGMENTS]):
                t = False
                for ccn in bidding_result[SEGMENTS][i + bias][CANDIDATES]:
                    if wcn[WINNING_COMPANY_NAME][2] == ccn[CANDIDATE_COMPANY_NAME][2]:
                        t = True
                        break
                if t is True:
                    bidding_result[SEGMENTS][i + bias][WINNER] = wcn
                    i += 1
                else:
                    bias += 1
            else:
                bidding_result[SEGMENTS].append(win_result[SEGMENTS][i])
                i += 1

    # 获取标段名
    t = u"".join(doc)
    if u"标段" in t:
        name_format = u"第{0}标段"
    elif u"包号" in t:
        name_format = u"包号{0}"
    else:
        name_format = u"合同包{0}"
    for i in range(len(bidding_result[SEGMENTS])):
        bidding_result[SEGMENTS][i][SEGMENT_NAME] = name_format.format(i + 1)

    # 去掉冗余信息
    for i in range(len(bidding_result[SEGMENTS])):
        winner = bidding_result[SEGMENTS][i][WINNER]
        if winner:
            for key in bidding_result[SEGMENTS][i][WINNER].keys():
                item = bidding_result[SEGMENTS][i][WINNER].get(key)
                if item:
                    bidding_result[SEGMENTS][i][WINNER][key] = item[2]
        candidates = bidding_result[SEGMENTS][i][CANDIDATES]
        if len(candidates) > 0:
            for j in range(len(candidates)):
                for key in candidates[j].keys():
                    item = candidates[j][key]
                    if item:
                        bidding_result[SEGMENTS][i][CANDIDATES][j][key] = item[2]

    return bidding_result


def assemble_bidding_result_info_new(doc_info, doc):
    """
    组合中标信息
    :param doc_info:
    :param doc:
    :return:
    """
    bidding_result = {}

    # 找到总中标金额
    total_wmn = doc_info.get(TOTAl_WINNING_MONEY)
    if isinstance(total_wmn, list) and len(total_wmn) > 0:
        max_pro = max([it[3] for it in total_wmn])
        total_wmn = [it for it in total_wmn if it[3] == max_pro]
        if max_pro >= 1:
            bidding_result[TOTAl_WINNING_MONEY] = total_wmn[0][2]
            delete_from_doc_info_items(doc_info, total_wmn)
        else:
            bidding_result[TOTAl_WINNING_MONEY] = None

    # 找到专家名表
    expert_names = doc_info.get(EXPERT_NAMES)
    if isinstance(expert_names, list) and len(expert_names) > 0:
        max_pro = max([it[3] for it in expert_names])
        expert_names = [it for it in expert_names if it[3] == max_pro]
        if max_pro >= 1:
            bidding_result[EXPERT_NAMES] = ",".join([x[2] for x in expert_names])
            delete_from_doc_info_items(doc_info, expert_names, compare_dim=[2])
        else:
            bidding_result[EXPERT_NAMES] = None

    def clear_bidding_result(info, field_name):
        values = info.get(field_name)
        if isinstance(values, list) and len(values) > 0:
            max_p = max([tt[3] for tt in values])
            de_values = [tt for tt in values if tt[3] == max_p]
            if max_p >= 1:
                delete_from_doc_info_items(doc_info, de_values)
                doc_info[field_name] = de_values

    def drop_items_pro(items):
        result = []
        for itm in items:
            mark = True
            for r in result:
                if itm[0] == r[0] and itm[1] == r[1] and itm[2] == r[2]:
                    mark = False
                    break
            if mark:
                result.append((itm[0], itm[1], itm[2]))
        return result

    def find_best_match_item(values_1, values_2):
        result = {}
        if len(values_1) * len(values_2) == 0:
            return result

        match_table = []
        for val_1 in values_1:
            tt = []
            line_idx_1 = val_1[0]
            for val_2 in values_2:
                line_idx_2 = val_2[0]
                comm_pref = commonprefix([doc[line_idx_1], doc[line_idx_2]])
                comm_pref = comm_pref[:(comm_pref.rfind(">>") + 1)]
                tt.append(comm_pref)
            match_table.append(tt)

        max_x_len = []
        max_y_len = []
        for row in match_table:
            max_len = max([len(p) for p in row])
            max_x_len.append(max_len)
            if len(max_y_len) == 0:
                max_y_len = [len(p) for p in row]
            else:
                max_y_len = [max(p, len(q)) for p, q in zip(max_y_len, row)]

        for i, row in enumerate(match_table):
            for j, col in enumerate(row):
                if len(col) == max_x_len[i] == max_y_len[j]:
                    if col not in result:
                        result[col] = {"field_1": [], "field_2": []}
                    if values_1[i] not in result[col]["field_1"]:
                        result[col]["field_1"].append(values_1[i])
                    if values_2[j] not in result[col]["field_2"]:
                        result[col]["field_2"].append(values_2[j])

        return result

    clear_fields = [WINNING_COMPANY_NAME, CANDIDATE_COMPANY_NAME, WINNING_COMPANY_ADDRESS, CANDIDATE_COMPANY_ADDRESS]
    for field in clear_fields:
        clear_bidding_result(doc_info, field)

    # 找到所有公司名字和中标金额
    companies = doc_info.get(WINNING_COMPANY_NAME, []) + doc_info.get(CANDIDATE_COMPANY_NAME, [])
    moneies = doc_info.get(WINNING_MONEY, []) + doc_info.get(CANDIDATE_MONEY, [])

    best_match = find_best_match_item(drop_items_pro(companies), drop_items_pro(moneies))

    cand_result, cdt_mn = assemble_candidate_info_new(doc_info, doc)
    bidding_result.update(cand_result)

    # 从可能中标公司中删除所有不是候选公司的公司名
    if len(cand_result[SEGMENTS]) > 0 and len(cand_result[SEGMENTS][0][CANDIDATES]) > 0:
        cand = []
        for seg in cand_result[SEGMENTS]:
            cand += seg[CANDIDATES]
        wcn = [x for x in doc_info[WINNING_COMPANY_NAME]]
        for cn in wcn:
            # t = False if cn[3] < 1 else True
            t = False
            for it in cand:
                ccn = it[CANDIDATE_COMPANY_NAME]
                if ccn[2] == cn[2]:
                    t = True
            if t is False:
                doc_info[WINNING_COMPANY_NAME].remove(cn)

    win_result, win_mn = assemble_winner_info_new(doc_info, doc)

    # 根据最佳的公司名和金额匹配结果来组合
    candidate_money = {"money": cdt_mn}
    win_com = [seg[WINNER][WINNING_COMPANY_NAME] for seg in win_result[SEGMENTS] if seg[WINNER]]
    matched_company_money = match_company_money(win_com, win_mn, best_match)
    for i in range(len(win_result[SEGMENTS])):
        t = win_result[SEGMENTS][i][WINNER]
        money = matched_company_money.get(t[WINNING_COMPANY_NAME])
        if money:
            delete_from_doc_info_items(candidate_money, [money])
        win_result[SEGMENTS][i][WINNER][WINNING_MONEY] = money

    cdt_com = []
    for seg in cand_result[SEGMENTS]:
        cdt_com += [cand[CANDIDATE_COMPANY_NAME] for cand in seg[CANDIDATES]]
    cdt_mn = candidate_money["money"]
    matched_company_money = match_company_money(cdt_com, cdt_mn, best_match)
    for i in range(len(cand_result[SEGMENTS])):
        for j in range(len(cand_result[SEGMENTS][i][CANDIDATES])):
            t = cand_result[SEGMENTS][i][CANDIDATES][j]
            cand_result[SEGMENTS][i][CANDIDATES][j][CANDIDATE_MONEY] = matched_company_money.get(
                t[CANDIDATE_COMPANY_NAME])

    # 将中标公司分段
    if len(win_result[SEGMENTS]) > 0:
        i, bias = 0, 0
        while i < len(win_result[SEGMENTS]):
            wcn = win_result[SEGMENTS][i][WINNER]
            not_in_candidates = False
            if i + bias < len(bidding_result[SEGMENTS]):
                t = False
                for ccn in bidding_result[SEGMENTS][i + bias][CANDIDATES]:
                    if wcn[WINNING_COMPANY_NAME][2] == ccn[CANDIDATE_COMPANY_NAME][2]:
                        t = True
                        break
                if t is True:
                    # 根据候选单位的投标金额补全中标公司的中标金额
                    if not wcn[WINNING_MONEY] and ccn[CANDIDATE_MONEY]:
                        wcn[WINNING_MONEY] = ccn[CANDIDATE_MONEY]
                    bidding_result[SEGMENTS][i + bias][WINNER] = wcn
                    next_step = (i + 1, bias)
                else:
                    not_in_candidates = True
                    next_step = (i, bias + 1)
            else:
                not_in_candidates = True
                next_step = (i + 1, bias)

            if not_in_candidates:
                if i + bias > 0:
                    b_wcn = bidding_result[SEGMENTS][i + bias - 1][WINNER]
                    if wcn[WINNING_COMPANY_NAME][2] == b_wcn[WINNING_COMPANY_NAME][2]:
                        if not wcn[WINNING_MONEY] or not b_wcn[WINNING_MONEY] or \
                                        wcn[WINNING_MONEY][2][MONEY_AMOUNT] != b_wcn[WINNING_MONEY][2][MONEY_AMOUNT]:
                            bidding_result[SEGMENTS][i + bias - 1][WINNER] = b_wcn if b_wcn[WINNING_MONEY] else wcn
                            next_step = (i + 1, bias - 1)
                if next_step == (i + 1, bias):
                    bidding_result[SEGMENTS].append(win_result[SEGMENTS][i])
            i, bias = next_step

    # 获取标段名
    t = u"".join(doc)
    if u"标段" in t:
        name_format = u"第{0}标段"
    elif u"包号" in t:
        name_format = u"包号{0}"
    else:
        name_format = u"合同包{0}"
    for i in range(len(bidding_result[SEGMENTS])):
        bidding_result[SEGMENTS][i][SEGMENT_NAME] = name_format.format(i + 1)

    # 去掉冗余信息
    for i in range(len(bidding_result[SEGMENTS])):
        winner = bidding_result[SEGMENTS][i][WINNER]
        if winner:
            for key in bidding_result[SEGMENTS][i][WINNER].keys():
                item = bidding_result[SEGMENTS][i][WINNER].get(key)
                if item:
                    bidding_result[SEGMENTS][i][WINNER][key] = item[2]
        candidates = bidding_result[SEGMENTS][i][CANDIDATES]
        if len(candidates) > 0:
            for j in range(len(candidates)):
                for key in candidates[j].keys():
                    item = candidates[j][key]
                    if item:
                        bidding_result[SEGMENTS][i][CANDIDATES][j][key] = item[2]

    return bidding_result


# **************** END 组合信息 END ****************  #
# -------------------------------------------------  #

# 解析公告文档
def analysis_announce_doc(document, pre_info, src_html):
    """
    从已经分解了的html文档中找到：中标时间、中标公司、中标金额(单位)
    :param document:
    :param pre_info:
    :param src_html:
    :return: return example, type = dict
        {
            WINNING_TS:"2016-01-02",
            DEAL_TS: "2016-01-02",
            PROJECT_NAME: "*****",
            PURCHASER_NAME: "****",
            ......
            AGENT_NAME: "",
            EXPERT_NAMES: "高**, 王**, 李**",
            TOTAl_WINNING_MONEY: {MONEY_AMOUNT:20000 ,MONEY_UNIT: "", MONEY_CURRENCY:""}
            SEGMENTS:[
                {
                    SEGMENT_NAME: "一包",
                    WINNER: {COMPANY_NAME: "",
                             COMPANY_ADDRESS: "",
                             WINNING_MONEY: {MONEY_AMOUNT: 2130.1, MONEY_UNIT: "", MONEY_CURRENCY:""}}
                    CANDIDATES:
                        [
                             {COMPANY_NAME: "",
                             COMPANY_ADDRESS: "",
                             WINNING_MONEY: {MONEY_AMOUNT: 2130.1, MONEY_UNIT: "", MONEY_CURRENCY:""},
                             RANK: 1},
                             ......
                             {COMPANY_NAME: "",
                             COMPANY_ADDRESS: "",
                             WINNING_MONEY: {MONEY_AMOUNT: 2130.1, MONEY_UNIT: "", MONEY_CURRENCY:""},
                             RANK: 2}
                        ]
                }
                ......
            ]
        }
    """
    if len(document) == 0:
        result = result_template()
        for key, val in pre_info.items():
            if key in result and val:
                result[key] = val
        return result

    doc_info = get_doc_info(document, src_html)

    # 结合已经知道的信息 pre_info 对文档进行处理
    # 将已经确定的信息绑定到 doc_info 上
    for key, value in pre_info.items():
        if key in doc_info and isinstance(value, (unicode, str)) and len(value) > 0:
            items = doc_info.get(key)
            if isinstance(items, list) and len(items) > 0:
                t = []
                for it in items:
                    line_idx, pos_idx, val, pro = it
                    if val == value:
                        t.append((line_idx, pos_idx, val, 1))
                        break
                delete_from_doc_info_items(doc_info, t, compare_dim=[2])
                doc_info[key] = t

    # 对各部分信息进行组合
    announce_info = assemble_announce_info(doc_info, document)
    project_info = assemble_project_info(doc_info, document)
    purchaser_info = assemble_purchaser_info(doc_info, document)
    agent_info = assemble_agent_info(doc_info, document)
    result_info = assemble_bidding_result_info_new(doc_info, document)

    # 将所有解析好的信息放到结果字典
    result = result_template()
    result.update(announce_info)
    result.update(project_info)
    result.update(purchaser_info)
    result.update(agent_info)
    result.update(result_info)

    # 将已知信息放入结果字典
    for key, val in pre_info.items():
        if key in result and val:
            result[key] = val

    # 对提取的信息进行验证
    # 1、ANNOUNCED_TS在所有时间之前

    # # 2、总中标金额是所有中标公司投标金额之和
    # if result[TOTAl_WINNING_MONEY]:
    #     unit = result[TOTAl_WINNING_MONEY][MONEY_UNIT]
    #     amount = result[TOTAl_WINNING_MONEY][MONEY_AMOUNT]
    #     for seg in result[SEGMENTS]:
    #         if seg[WINNER]:
    #             if seg[WINNER][WINNING_MONEY]:
    #                 if seg[WINNER][WINNING_MONEY][MONEY_UNIT] != unit:
    #                     break
    if not result[TOTAl_WINNING_MONEY]:
        total_currency = u"人民币"
        total_unit = u"元"
        total_amount = None
        valid = True
        for seg in result[SEGMENTS]:
            if seg[WINNER]:
                if seg[WINNER][WINNING_MONEY]:
                    currency = seg[WINNER][WINNING_MONEY][MONEY_CURRENCY]
                    unit = seg[WINNER][WINNING_MONEY][MONEY_UNIT]
                    amount = seg[WINNER][WINNING_MONEY][MONEY_AMOUNT]
                    if total_unit != unit or total_currency != currency:
                        valid = False
                        break
                    if total_amount is None:
                        total_amount = 0
                    total_amount += amount
        if total_amount < 1e9 and valid and total_amount:
            total_winning_money = money_template()
            total_winning_money[MONEY_AMOUNT] = total_amount
            total_winning_money[MONEY_UNIT] = total_unit
            total_winning_money[MONEY_CURRENCY] = total_currency
            result[TOTAl_WINNING_MONEY] = total_winning_money

    # 3、项目预算总金额大于等于总中标金额

    # # 4、公司投标金额不能太大，以1e9为界
    # for seg in result[SEGMENTS]:
    #     if seg[WINNER]:
    #         if seg[WINNER][WINNING_MONEY]:
    #             if seg[WINNER][WINNING_MONEY][MONEY_UNIT] == u"元" and seg[WINNER][WINNING_MONEY][MONEY_AMOUNT] > 1e9:
    #                 result["check_money_amount"] = False
    #                 break
    #     if seg[CANDIDATES]:
    #         for cand in seg[CANDIDATES]:
    #             if cand[CANDIDATE_MONEY]:
    #                 if cand[CANDIDATE_MONEY][MONEY_UNIT] == u"元" and cand[CANDIDATE_MONEY][MONEY_AMOUNT] > 1e9:
    #                     result["check_money_amount"] = False
    #                     break

    # 5、公司名字长度不能长于40个字符

    # 6、分包候选供应商排序，如果有必须从1开始
    remove_segs = []
    for seg in result[SEGMENTS]:
        ranks = [cdt[CANDIDATE_RANK] for cdt in seg[CANDIDATES] if cdt.get(CANDIDATE_RANK)]
        if len(ranks) > 0 and 1 not in ranks:
            remove_segs.append(seg)
    for seg in remove_segs:
        result[SEGMENTS].remove(seg)

    return result
