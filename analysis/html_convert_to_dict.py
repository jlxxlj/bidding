# coding=utf-8
# author="Jianghua Zhao"

import re
import bs4
import sys

from collections import OrderedDict

import util
from html_purify import build_beautifulsoup

sys.setrecursionlimit(10000)

INDEX_HANDLES = []
HANDLE_FMT = ">{0}<"
INDEX_HANDLES.append(("CN", u"[零一二三四五六七八九十百]+", util.convert_cn_number))
INDEX_HANDLES.append(("EN", u"[0-9]+", lambda x: int("0" + x.lstrip("0"))))
INDEX_HANDLES.append(("RMU", u"[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ]", lambda x: u"ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ".index(x) + 1))
INDEX_HANDLES.append(("RMD", u"[ⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹⅺⅻ]", lambda x: u"ⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹⅺⅻ".index(x) + 1))
INDEX_HANDLES.append(("ABU", u"[A-Z]", lambda x: ord(x) - ord("A")))
INDEX_HANDLES.append(("ABD", u"[a-z]", lambda x: ord(x) - ord("a")))


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
                child = re.sub(u"\s", "", child)
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
    只提取能够被匹配的编号
    :param paragraphs: All indexes in html document paragraphs
    :return:  A list of tuple for each paragraphs, tuple as (mode, index)
    """
    p_len = len(paragraphs)

    p_mode = []
    p_index = []
    for i in range(p_len):
        p_mode.append(None)
        p_index.append(None)
        if paragraphs[i].name == "p":
            text = paragraphs[i].get_text().strip()
            for key, reg, cvt in INDEX_HANDLES:
                indexes = re.findall(reg, text)
                if len(indexes) > 0:
                    pre = text.split(indexes[0])[0]
                    mode = pre + HANDLE_FMT.format(key)
                    if len(pre) <= 3 and (p_mode[i] is None or len(p_mode[i]) > len(mode)):
                        p_mode[i] = mode
                        p_index[i] = cvt(indexes[0])

    find_index = []
    for i in range(p_len):
        fmt, num = None, None
        if p_mode[i]:
            for j in range(p_len):
                if i != j and p_mode[j] and p_mode[i] == p_mode[j]:
                    fmt = p_mode[i]
                    num = p_index[i]
                    break
        find_index.append((fmt, num))

    return find_index


def match(pre_index, sub_index):
    """
    判断两个段落的编号是否匹配
    如果是同等的段落应该满足两个要求：
    1.编号模式相同 2.编号递增
    :param pre_index:
    :param sub_index:
    :return:
    """
    if pre_index[0] is None or sub_index[0] is None:
        return False
    elif pre_index[0] != sub_index[0]:  # 1.编号模式相同
        return False
    elif pre_index[1] != sub_index[1] - 1:  # 2.编号递增
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
    length = len(index)
    matched_index = [[None, None] for i in range(length)]
    # matched = [False for i in range(length)]
    for i in range(1, length):
        j = i - 1
        while j >= 0:  # 从上一段依次向前匹配
            if match(index[j], index[i]):
                if not matched_index[j][1]:  # 被匹配过的编号不再被匹配
                    # matched[j] = True
                    matched_index[i][0] = j
                    matched_index[j][1] = i
                    break
            if matched_index[j][0]:
                j = matched_index[j][0]
            else:
                j -= 1

    return matched_index


def segment_matched_index(indexes, start, end):
    """
    # 根据编号匹配情况进行分节
    # 每一节必须以有编号的段开始
    :param indexes:
    :param end:
    :param start:
    :return:
    """
    res = []
    i = start
    while i < end:
        if indexes[i][0] is None and indexes[i][1] is None:
            res.append(i)
            i += 1
        else:
            res.append(i)
            if indexes[i][1]:
                t = indexes[i][1]
            else:
                t = end
            if i + 1 < t:
                res.append(segment_matched_index(indexes, i + 1, t))
            i = t

    return res


def segment_matched_index_by_keywords(indexes, start, end, paragraphs):
    """
    # 根据编号匹配情况进行分节
    # 每一节必须以有编号的段开始
    :param indexes:
    :param end:
    :param start:
    :param paragraphs:
    :return:
    """
    res = []

    has_sub_seg = False
    i = start
    while i < end:
        if indexes[i][0] is None and indexes[i][1] is None:
            res.append(i)
            i += 1
        else:
            has_sub_seg = True
            res.append(i)
            if indexes[i][1]:
                t = indexes[i][1]
            else:
                t = end
            if i + 1 < t:
                res.append(segment_matched_index_by_keywords(indexes, i + 1, t, paragraphs))
            i = t

    # 按编号不能再分的段，根据关键字来分段
    if has_sub_seg is False:
        res = []
        t_res = []
        for idx in range(start, end):
            p_text = paragraphs[idx].get_text().strip()
            typ = util.type_of_text(p_text.rstrip(u"："))
            if typ == "k" and paragraphs[idx].name == "p" and p_text.endswith(u"："):
                if len(t_res) > 0:
                    if len(res) == 0:
                        res = t_res
                    else:
                        res.append(t_res)
                res.append(idx)
                t_res = []
            else:
                t_res.append(idx)
        if len(t_res) > 0:
            if len(res) == 0:
                res = t_res
            else:
                res.append(t_res)
    else:
        if end - start > 1 and paragraphs[start].name == "p" and indexes[start][0] is None and indexes[start][
            1] is None:
            head_p = paragraphs[start].get_text().strip()
            typ = util.type_of_text(head_p.rstrip(u"："))
            if head_p.endswith(u"：") and typ == "k":
                res = [res[0], res[1:]]

    return res


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


def get_paragraph_prefix(paragraphs, matched_index):
    """
    找到每段前面可以匹配的编号前缀
    :param paragraphs:
    :param matched_index:
    :return:
    """
    length = len(paragraphs)

    p_text = [p.get_text().strip() for p in paragraphs]

    splited_p_text = [[None, None, None] for i in range(length)]
    for i in range(length):
        for key, reg, cvt in INDEX_HANDLES:
            t = re.findall(reg, p_text[i])
            if len(t) > 0:
                if splited_p_text[i][1] is None or p_text[i].index(splited_p_text[i][1]) > p_text[i].index(t[0]):
                    splited_p_text[i][1] = t[0]
        if splited_p_text[i][1]:
            splited_p_text[i][0], splited_p_text[i][2] = p_text[i].split(splited_p_text[i][1], 1)

    prefixes = [None for i in range(length)]
    for i in range(length):
        # 计算相互匹配的编号段个数
        idx = [i]
        while not prefixes[i] and matched_index[idx[-1]][1]:
            idx.append(matched_index[idx[-1]][1])
        count = len(idx)
        if count < 2:
            continue
        # 最短的段的文本长度
        texts = [splited_p_text[k][2] for k in idx]
        min_len = len(texts[0])
        for k in range(count):
            min_len = min(min_len, len(texts[k]))
        # 计算相同的编号前缀
        j = 0
        for j in range(min_len):
            t = True
            for k in range(count - 1):
                if texts[k][j] != texts[k + 1][j]:
                    t = False
                    break
            if t is False:
                break
        suff = texts[0][:j]
        suff = ""

        for k in idx:
            prefix = splited_p_text[k][0] + splited_p_text[k][1] + suff
            prefixes[k] = prefix

    return prefixes


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
    items = split_text(u"(?<=[\u4e00-\u9fa5])(?:%s)" % "|".join(util.KEY_VALUE_SEPARATOR), text)

    # res = OrderedDict()
    res = []
    if len(items) == 0:
        pass
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
                if value == "":
                    value = items[i]
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


def analysis_table_key_value_1(t):
    # 单元格值, 单元格类型, 单元格rect(x, y, row, col)范围, 接受方向"UD"和"LR"两种
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
                num = re.findall("\d+", td["colspan"])
                if len(num) > 0:
                    cell_size_y = int(num[0])
            if "rowspan" in td.attrs:
                num = re.findall("\d+", td["rowspan"])
                if len(num) > 0:
                    cell_size_x = int(num[0])
            cell_rect = (row_num, row_num + cell_size_x, col_num, col_num + cell_size_y)
            td_element = [td_res, text_type, cell_rect, None]
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

    return table


def analysis_table_key_value_2(table):
    res = []  # 根据确定的关键字和值所在的位置，从后向前查看包含了值的所有可能关键字
    for row_num in range(len(table)):
        for col_num in range(len(table[row_num])):
            td_res = table[row_num][col_num][0]
            text_type = table[row_num][col_num][1]
            value_rect = table[row_num][col_num][2]
            if text_type in ("v", "kv"):
                # 从后向前查看包含了值的所有可能关键字
                x, y = row_num, col_num
                find_keyword_count = 0
                for i in range(x, -1, -1):
                    if i == row_num:
                        y = col_num
                    else:
                        y = len(table[i])
                    for j in range(y - 1, -1, -1):
                        if table[i][j][1] is not "k":
                            continue
                        key_rect = table[i][j][2]
                        direct = table[i][j][3]
                        if key_rect[0] <= value_rect[0] and key_rect[1] >= value_rect[1] and key_rect[3] <= value_rect[
                            2] and (direct is None or direct == "LR"):
                            if text_type in ("v", "kv") \
                                    or key_rect[0] + value_rect[1] - key_rect[1] - value_rect[0] < 0:
                                text_type = "k"
                                td_res = [table[i][j][0][0] + ">>" + x for x in td_res]
                                value_rect = (min(key_rect[0], value_rect[0]), max(key_rect[1], value_rect[1]),
                                              min(key_rect[2], value_rect[2]), max(key_rect[3], value_rect[3]))
                                find_keyword_count += 1
                                table[row_num][col_num][3] = "LR"
                                direct = "LR"
                        elif key_rect[2] <= value_rect[2] and key_rect[3] >= value_rect[3] and key_rect[1] <= \
                                value_rect[
                                    0] and (direct is None or direct == "UD"):
                            if text_type in ("v", "kv") \
                                    or key_rect[2] + value_rect[3] - key_rect[3] - value_rect[2] < 0:
                                text_type = "k"
                                td_res = [table[i][j][0][0] + ">>" + x for x in td_res]
                                value_rect = (min(key_rect[0], value_rect[0]), max(key_rect[1], value_rect[1]),
                                              min(key_rect[2], value_rect[2]), max(key_rect[3], value_rect[3]))
                                find_keyword_count += 1
                                table[row_num][col_num][3] = "UD"
                                direct = "UD"
                        elif find_keyword_count == 1 and table[row_num][col_num][3] == "LR":  # 处理具有二维描述的表格，上方和左方都有它的关键字
                            t_value_rect = table[row_num][col_num][2]

                            if key_rect[2] <= t_value_rect[2] and \
                                    key_rect[3] >= t_value_rect[3] and \
                                    key_rect[1] <= t_value_rect[0] and \
                                    (direct is None or direct == "UD"):
                                text_type = "k"
                                td_res = [table[i][j][0][0] + ">>" + x for x in td_res]
                                value_rect = (min(key_rect[0], value_rect[0]), max(key_rect[1], value_rect[1]),
                                              min(key_rect[2], value_rect[2]), max(key_rect[3], value_rect[3]))
                                find_keyword_count += 1
                                table[row_num][col_num][3] = "UD"
                                direct = "UD"

                        table[i][j][3] = direct
                # 添加到结果集
                res += td_res
    return res


def analysis_table_key_value(t):
    """
    # 首先分析单元表格是关键字还是值，以及每个单元格在表格中所处的位置
    # 根据确定的关键字和值所在的位置，从后向前查看包含了值的所有可能关键字
    :param t:
    :return:
    """
    table = analysis_table_key_value_1(t)
    res = analysis_table_key_value_2(table)
    return res


from html_dict_analysis import element_obtain_regular_func_table

FUNC_TAB = element_obtain_regular_func_table()


def split_key_value(paragraphs, prefixes):
    """
    # 将paragraphs中的键值对分割出来
    :param paragraphs:
    :param prefixes:
    :return:
    """
    # res_dict = OrderedDict()
    res = []

    i, length = 0, len(paragraphs)
    while i < length:
        if paragraphs[i].name == "p":
            t_res = analysis_p_key_value(paragraphs[i])
        elif paragraphs[i].name == "table":
            t_res = analysis_table_key_value(paragraphs[i])
            t_res = ["table>>" + it for it in t_res]
        else:
            raise Exception("unexpected bs4.Tag.name=%s" % paragraphs[i].name)

        if i + 1 == length or isinstance(paragraphs[i + 1], bs4.Tag):
            res += t_res
            i += 1
        elif isinstance(paragraphs[i + 1], list):
            t = split_key_value(paragraphs[i + 1], prefixes[i + 1])
            if ">>" in t_res[0]:
                prefix = prefixes[i]
                t = t_res + t
            elif len(FUNC_TAB["company_name"][0](t_res[0])) > 0:
                prefix = prefixes[i]
                t = t_res + t
            elif len(FUNC_TAB["money"][0](t_res[0])) > 0:
                prefix = prefixes[i]
                t = t_res + t
            elif len(FUNC_TAB["address"][0](t_res[0])) > 0:
                prefix = prefixes[i]
                t = t_res + t
            else:
                prefix = t_res[0]
            prefix = prefix if prefix else ""
            res += [prefix + ">>" + r for r in t]
            i += 2
        else:
            raise Exception("unexpected item type, accept list and bs4.Tag")

    return res


def analysis_html(html):
    """
    # 文本分析，将文本按键值对分割出来
    :param html:
    :return:
    """
    if isinstance(html, bs4.Tag):
        bs = html
    else:
        bs = build_beautifulsoup(html)

    paragraphs = find_paragraphs(bs)
    index = get_index(paragraphs)
    matched_index = match_index(index)

    seg_index = segment_matched_index_by_keywords(matched_index, 0, len(matched_index), paragraphs)
    seg_paras = convert_list_to_segments(paragraphs, seg_index)

    prefixes = get_paragraph_prefix(paragraphs, matched_index)
    seg_prefixes = convert_list_to_segments(prefixes, seg_index)



    result = split_key_value(seg_paras, seg_prefixes)
    for i in range(len(result)):
        result[i] = re.sub(u"[\s 　]+", u"", result[i])
        result[i] = result[i].replace(u"(", u"（")
        result[i] = result[i].replace(u")", u"）")
    return result


if __name__ == '__main__':
    content = '''
    HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN"<html><head><title>青海省招标投标网 ·        “东川工业园区工业废水处理厂及配套管网工程”10KV供配电设备项目东川工业园区工业废水处理厂及配套管网工程”10KV供配电设备项目</title></head><body><table><tr><td>HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN"<html><head><title>青海省招标投标网</title></head><body><table><tr><td><table><tr><td></td><td><ul><li>首页</li><li>办事指南</li><li>交易信息<ul><li>工程建设</li><li>政府采购</li><li>产权交易</li><li>矿产权交易</li><li>药品采购</li></ul></li><li>信用平台<ul><li>光荣榜</li><li>曝光台</li><li>不良行为记录</li></ul></li><li>数据统计</li><li>平台介绍</li><li>诚信库查询</li><li>站点切换<ul><li>西宁市</li><li>海东市</li></ul></li></ul></td></tr></table></td></tr></table></body></html></td></tr></table></body></html><li>海西州</li><li>海南州</li><li>海北州</li><li>黄南州</li><li>果洛州</li><li>玉树州</li><li>格尔木</li><li>返回中心</li><li>新版系统</li><td></td><tr><td><table><tr><td></td><td><table><tr><td></td><td></td><td><iframe></iframe></td></tr></table></td><td><table><tr><td>工程建设</td><td>政府采购</td><td>药品采购</td><td>产权交易</td><td>矿业权交易</td></tr></table></td><td></td></tr></table></td></tr><table><tr><td><table><tr><td><table><tr><td></td><td><table><tr><td></td><td><font>您现在的位置：</font>首页<font>&gt;&gt;交易信息&gt;&gt;工程建设&gt;&gt;中标公示</font></td></tr></table></td></tr></table></td></tr><tr><td><table><tr><td><font>“东川工业园区工业废水处理厂及配套管网工程”10KV供配电设备项目东川工业园区工业废水处理厂及配套管网工程”10KV供配电设备项目</font><br/><br/></td></tr><tr><td><font>【信息时间：                      2018/3/21 11:18:02                        阅读次数：                                            】【我要打印】【关闭】</font></td></tr><tr><td><div>HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"<html><head><title>Report</title></head><body><table><tr><td colspan="3"><div>中标人公示</div></td></tr><tr><td><div>项目名称</div></td><td colspan="2"><div>“东川工业园区工业废水处理厂及配套管网工程”10KV供配电设备项目</div></td></tr><tr><td><div>招标人</div></td><td colspan="2"><div>西宁经济技术开发区发展集团有限公司</div></td></tr><tr><td><div>招标代理机构</div></td><td colspan="2"><div>西宁城宏建设工程招标有限责任公司</div></td></tr><tr><td><div>招标编号</div></td><td colspan="2"><div>E6301000076017763</div></td></tr><tr><td><div>建设地点</div></td><td colspan="2"><div>青海省 西宁州(市)     县(或区)境内</div></td></tr><tr><td><div>招标主要内容</div></td><td colspan="2"><div>该工程位于东川工业园区峡口路以西、八一路以南，项目计划对“东川工业园区工业废水处理厂及配套管网工程”10KV供配电设备工程</div></td></tr><tr><td><div>招标方式</div></td><td colspan="2"><div>公开招标</div></td></tr><tr><td><div>招标公告发布时间</div></td><td colspan="2"><div>2017年11月21日</div></td></tr><tr><td><div>开标时间</div></td><td colspan="2"><div>2018年03月20日 9:00</div></td></tr><tr><td><div>开标地点</div></td><td colspan="2"><div>西宁市公共资源交易中心</div></td></tr><tr><td><div>最高限价（元）</div></td><td colspan="2"><div>/</div></td></tr><tr><td><div>中标人</div></td><td colspan="2"><div>青海鸿祥建设工程有限公司</div></td></tr><tr><td><div>中标报价（元）</div></td><td colspan="2"><div>3891733.2400</div></td></tr><tr><td><div>工期或交货期或服务期（天）</div></td><td colspan="2"><div>30</div></td></tr><tr><td><div>项目负责人（经理）</div></td><td colspan="2"><div>张国伟 资质等级：贰级建造师/0000410</div></td></tr><tr><td><div>公示期限</div></td><td colspan="2"><div>开始日期：2018年03月21日 结束日期：2018年03月23日</div></td></tr><tr><td><div>监督部门及联系电话</div></td><td colspan="2"><div>监督单位：东川工业园区建设局、东川工业园区工商分局 0971-8130992、8804418</div></td></tr><tr><td></td><td></td><td><div>2018年03月21日</div></td></tr></table></body></html></div></td></tr></table></td></tr></table></td></tr></table>
    '''
    print analysis_html(content)