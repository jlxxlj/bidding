# -*- coding: utf-8 -*-
# __author__ = 'Jianghua Zhao'
# jianghua.zhao@socialcredits.cn

import re
import bs4
import sys

import util
from html_preprocess import build_beautifulsoup

sys.setrecursionlimit(10000)


def find_paragraphs(tag):
    """
    查找标签下所以需要分析的自然段
    这个将<table>认为是一个特殊的自然段进行单独处理
    :param tag:  待处理标签
    :return:
    """
    paragraphs = []
    for child in tag.children:
        if not isinstance(child, bs4.Tag):
            if isinstance(child, bs4.NavigableString):
                t = "<p>" + child + "</p>"
                t = build_beautifulsoup(t)
                paragraphs.append(t.contents[0])
            else:
                continue
        elif child.name == "table":
            paragraphs.append(child)
        else:
            paragraphs += find_paragraphs(child)
    return paragraphs


def get_index(paragraphs):
    """
    获取每段文本前面的编号，如汉字数字或阿拉伯数字
    只提取由标点符号和空白围绕的编号
    :param paragraphs: All indexes in html document paragraphs
    :return:  A list of dict for each paragraphs, dict as {"number": number, "fmt": fmt, "mode": mode}
    """
    index = []
    for paragraph in paragraphs:
        if paragraph.name == "p":
            text = paragraph.get_text()
            number, fmt, mode = None, None, ""
            _ST_ = 0
            for t in text:
                if _ST_ == 0:  # 开始查找编号
                    if t in util.DICT_NUMBER:
                        number = util.DICT_NUMBER[t]
                        fmt = "AL"
                        t = "N"  # "N" 表示是一个编号
                        _ST_ = 1
                    elif t in util.DICT_CN_SIMPLE_NUMBER:
                        number = util.DICT_CN_SIMPLE_NUMBER[t]
                        fmt = "CN"
                        t = "N"  # "N" 表示是一个编号
                        _ST_ = 1
                    elif t not in util.CN_PUNCTUATION + util.EN_PUNCTUATION + util.BLANK:  # 如果不是符号，就退出查找编号
                        break
                elif _ST_ == 1:  # 找到编号，查找是否还有后续的数字
                    if t in util.DICT_NUMBER and fmt == "AL":  # 多个阿拉伯数字
                        number = 10 * number + util.DICT_NUMBER[t]
                        t = ""
                    elif t in util.DICT_CN_SIMPLE_NUMBER and fmt == "CN":  # 多个中文数字， 只考虑了十几的情况
                        number += util.DICT_CN_SIMPLE_NUMBER[t]
                        t = ""
                    elif t in util.CN_PUNCTUATION + util.EN_PUNCTUATION + util.BLANK:  # 如果不是符号，就退出查找编号
                        _ST_ = 2
                    else:
                        break
                elif _ST_ == 2:  # 编号数字查找完毕，判断编号是否结束
                    if t not in util.CN_PUNCTUATION + util.EN_PUNCTUATION + util.BLANK:  # 如果不是符号，就退出查找编号
                        break
                mode += t
            if number is not None:
                index.append({"number": number, "fmt": fmt, "mode": mode})
            else:
                index.append(None)
        else:
            index.append(None)
    return index


def match(pre_index, sub_index):
    """
    判断两个段落的编号是否匹配
    如果是同等的段落应该满足三个要求：
    1.编号递增 2.同一种编号体系 3.编号模式相同
    :param pre_index:
    :param sub_index:
    :return:
    """
    if pre_index is None or sub_index is None:
        return False
    elif pre_index["number"] != sub_index["number"] - 1:  # 1.编号递增
        return False
    elif pre_index["fmt"] != sub_index["fmt"]:  # 2.同一种编号体系
        return False
    elif pre_index["mode"] != sub_index["mode"]:  # 3.编号模式相同
        return False
    else:
        return True


def match_index(index):
    """
    对段落编号进行匹配, 找到每一段前面最先匹配的段落
    :param index:
    :return:
    """
    # 找到每一段前面最先匹配的段落
    if len(index) < 1:
        return []
    matched_index = [None]  # 第一段没有匹配项
    matched = [False]
    for i in range(1, len(index)):
        is_matched = False
        matched.append(False)
        for j in range(i - 1, -1, -1):  # 从上一段依次向前匹配
            if match(index[j], index[i]):
                if matched[j] is True:  # 被匹配过的编号不在被匹配
                    continue
                matched[j] = True
                is_matched = True
                matched_index.append(j)
                if matched_index[j] is None:  # 如果被匹配的到段是第一段，则让第一段匹配自己
                    matched_index[j] = j
                break
        if not is_matched:
            matched_index.append(None)

    return matched_index


def segment_matched_index(indexs, start, end, is_first_time_be_called=True):
    """
    # 根据编号匹配情况进行分节
    # 每一节必须以有编号的段开始
    :param indexs:
    :param start:
    :param end:
    :param is_first_time_be_called:
    :return:
    """
    if is_first_time_be_called:
        step_over = 0
        segs_index = []
    else:
        step_over = 1
        segs_index = [start]

    pre_index = None
    for i in range(start + step_over, end):
        if pre_index is None:
            if indexs[i] == i:
                pre_index = i
            else:
                segs_index.append(i)
        else:
            if indexs[i] == pre_index:
                pre_index = i
                ind = segment_matched_index(indexs, indexs[i], i, False)
                segs_index.append(ind)
    if pre_index is not None:
        ind = segment_matched_index(indexs, pre_index, end, False)
        segs_index.append(ind)
    return segs_index


def convert_list_to_segments(lst, segs_index):
    """
    # 将列表按分好节的标号进行分节
    :param lst:
    :param segs_index:
    :return:
    """
    segments = []
    for index in segs_index:
        if isinstance(index, list):
            segments.append(convert_list_to_segments(lst, index))
        else:
            segments.append(lst[index])
    return segments


def split_text(pattern, text):
    """
    按pattern给出的正则表达式对text进行分割, 去掉空白的结果
    :param pattern:
    :param text:
    :return:
    """
    items = re.split(pattern, text)
    items = [x.strip() for x in items if len(x.strip()) > 0]
    return items


def analysis_p_key_value(p):
    """
    # 分析段落里的关键字和值
    # 只考虑单一节点的情况，
    # 如果一段中存在多个键值分割符，且两个键值分割符之间还有足够
    # 宽度的空白，则将其再进行分割处理
    :param p:
    :return:
    """
    text = p.get_text().strip()
    items = split_text("|".join(util.KEY_VALUE_SEPARATOR), text)

    res = []
    if len(items) == 0:
        res = []
    elif len(items) == 1:
        res = [items[0]]
    elif len(items) == 2:
        res = [">>".join(items)]
    else:
        key, value = items[0], ""
        for i in range(1, len(items)):
            t = split_text(u"    |\t|\n", items[i])
            if len(t) > 1:
                value += t[0]
                res += [key + ">>" + value]
                key, value = "".join(t[1:]), ""
            else:
                value += ">>" + items[i]
        res += [key + ">>" + value]

    return res


def find_trs_children(tag):
    """
    找到标签下的直接tr标签
    :param tag:
    :return:
    """
    trs = []
    for child in tag.children:
        if isinstance(child, bs4.Tag):
            if child.name == "tr":
                trs.append(child)
            elif child.name != "table":
                trs += find_trs_children(child)
    return trs


def find_tds_children(tag):
    """
    找到标签下的直接td,th标签
    :param tag:
    :return:
    """
    trs = []
    for child in tag.children:
        if isinstance(child, bs4.Tag):
            if child.name in ("td", "th"):
                trs.append(child)
            elif child.name != "table":
                trs += find_trs_children(child)
    return trs


def analysis_table_key_value(t):
    """
    # 首先分析单元表格是关键字还是值，以及每个单元格在表格中所处的位置
    # 根据确定的关键字和值所在的位置，从后向前查看包含了值的所有可能关键字
    :param t:
    :return:
    """
    table = []  # 分析表格里的关键字和值以及单元格所处的位置
    row_num = 0  # 行号
    used_cols = []  # 由于rowspan>1或rowspan>1, 从而占用了的后续行中可用的列
    used_cols_content = []
    trs = find_trs_children(t)  # 找到table标签下的所有属于它的tr标签
    for tr in trs:
        row = []  # 当前row
        curr_row = []
        if len(used_cols) > 0:
            curr_row = used_cols[0]
            row = used_cols_content[0]
            used_cols = used_cols[1:]
            used_cols_content = used_cols_content[1:]
        col_num = 0
        tds = find_tds_children(tr)  # 找到tr标签下的所有属于它的td,th标签
        for td in tds:
            curr_row.sort(key=lambda x: x[0])
            for st, ed in curr_row:  # 找到列的开始位置
                if st - col_num <= 0:
                    col_num = ed

            text = td.get_text().strip()
            text_type = util.type_of_text(text)  # fun(text)
            if len(text) <= 30:
                td_res = [text]
            else:
                td_res = analysis_html(str(td))
            if len(td_res) > 1:  # 如果单元格分段大于1，则认为单元格内是值
                text_type = "v"
            elif len(td_res) <= 0:
                td_res = [text]
            cell_size_x, cell_size_y = 1, 1
            if "colspan" in td.attrs:
                cell_size_y = int(td["colspan"])
            if "rowspan" in td.attrs:
                cell_size_x = int(td["rowspan"])
            cell_rect = (row_num, row_num + cell_size_x, col_num, col_num + cell_size_y)
            td_element = (td_res, text_type, cell_rect)
            for x in range(cell_size_x - 1):
                if x >= len(used_cols):
                    used_cols.append([])
                    used_cols_content.append([])
                used_cols[x].append((col_num, col_num + cell_size_y))
                used_cols_content[x].append(td_element)
            row.append(td_element)
            curr_row.append((col_num, col_num + cell_size_y))
            col_num += cell_size_y
        row = sorted(row, key=lambda td_elmt: td_elmt[2][2])
        table.append(row)
        row_num += 1

    res = []  # 根据确定的关键字和值所在的位置，从后向前查看包含了值的所有可能关键字
    for row_num in range(len(table)):
        # items = dict(zip(table[0], table[row_num]))
        # res.update({"tr%d" % row_num: items})
        for col_num in range(len(table[row_num])):
            td_res = table[row_num][col_num][0]
            text_type = table[row_num][col_num][1]
            value_rect = table[row_num][col_num][2]
            if text_type in ("v", "kv"):
                # 从后向前查看包含了值的所有可能关键字
                x, y = row_num, col_num
                for i in range(x, -1, -1):
                    if i == row_num:
                        y = col_num
                    else:
                        y = len(table[i])
                    for j in range(y - 1, -1, -1):
                        if table[i][j][1] is not "k":
                            continue
                        key_rect = table[i][j][2]
                        if key_rect[0] <= value_rect[0] and key_rect[1] >= value_rect[1]:  # and key_rect[3] == value_rect[2]
                            if text_type in ("v", "kv") \
                                    or key_rect[0] + value_rect[1] - key_rect[1] - value_rect[0] < 0:
                                text_type = "k"
                                td_res = [table[i][j][0][0]+">>"+x for x in td_res]
                                value_rect = (min(key_rect[0], value_rect[0]), max(key_rect[1], value_rect[1]),
                                              min(key_rect[2], value_rect[2]), max(key_rect[3], value_rect[3]))
                        elif key_rect[2] <= value_rect[2] and key_rect[3] >= value_rect[3]:  # and key_rect[1] == value_rect[0]
                            if text_type in ("v", "kv") \
                                    or key_rect[2] + value_rect[3] - key_rect[3] - value_rect[2] < 0:
                                text_type = "k"
                                td_res = [table[i][j][0][0] + ">>" + x for x in td_res]
                                value_rect = (min(key_rect[0], value_rect[0]), max(key_rect[1], value_rect[1]),
                                              min(key_rect[2], value_rect[2]), max(key_rect[3], value_rect[3]))
                # 添加到结果集
                res += td_res
    return res


def split_key_value(paragraphs, index):
    """
    # 将paragraphs中的键值对分割出来
    :param paragraphs:
    :param index:
    :return:
    """

    # 先根据文本的分段来判断处理方式
    res = []
    if isinstance(paragraphs, bs4.Tag):
        if paragraphs.name == "p":
            res += analysis_p_key_value(paragraphs)
        elif paragraphs.name == "table":
            res += analysis_table_key_value(paragraphs)
    elif isinstance(paragraphs, list):
        if len(paragraphs) < 1:
            return res
        first_para = paragraphs[0]
        if isinstance(first_para, bs4.Tag):
            if first_para.name == "p":
                # 先确定第一段是否有编号
                if index[0] is None:  # 没有编号
                    for ps, ind in zip(paragraphs, index):
                        res += split_key_value(ps, ind)  # 将每一个段分别处理
                else:  # 有编号
                    # 考虑其是否是一个键值对
                    text = first_para.get_text()
                    items = split_text("|".join(util.KEY_VALUE_SEPARATOR), text)
                    if len(items) > 1:
                        # number = get_index(paragraphs[:1])[0]["number"]
                        index[0] = None
                        r = split_key_value(paragraphs, index)
                        # res += [str(number) + ">>" + x for x in r]
                        res += r
                    elif len(items) == 1:
                        if len(paragraphs) > 1:
                            r = split_key_value(paragraphs[1:], index[1:])
                            res += [items[0] + ">>" + x for x in r]
                        else:
                            res += [items[0]]
            elif first_para.name == "table":
                for ps, ind in zip(paragraphs, index):
                    res += split_key_value(ps, ind)
        elif isinstance(first_para, list):
            for ps, ind in zip(paragraphs, index):
                res += split_key_value(ps, ind)
    return res


def analysis_html(html):
    """
    # 文本分析，将文本按键值对分割出来
    :param html:
    :return:
    """
    bs = build_beautifulsoup(html)
    paragraphs = find_paragraphs(bs)

    index = get_index(paragraphs)
    matched_index = match_index(index)
    seg_index = segment_matched_index(matched_index, 0, len(matched_index))
    seg_paras = convert_list_to_segments(paragraphs, seg_index)
    seg_match_index = convert_list_to_segments(matched_index, seg_index)

    result = split_key_value(seg_paras, seg_match_index)

    return result
