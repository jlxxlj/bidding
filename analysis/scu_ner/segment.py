# -*- coding: utf-8 -*- 

# import logging
# logger = logging.getLogger(__name__)

import re
import lxml.html
import copy

# html_tag = re.compile(ur'''<([A-Za-z][A-Za-z0-9]*)\b[^>]*>(.*?)</\1>''',
#                flags=re.UNICODE|re.DOTALL|re.VERBOSE)
html_special = re.compile(ur'''<(style|script)\b[^>]*>(.*?)</\1>''',
                          flags=re.UNICODE | re.DOTALL | re.VERBOSE)
html_tag = re.compile(ur'''</?[A-Za-z][A-Za-z0-9]*\b[^>]*>''',
                      flags=re.UNICODE | re.DOTALL | re.VERBOSE)
# punctuation = re.compile(ur'''([\[\]\,?"\(\)+_*\/\\&\$#^@!%~`<>:;\{\}？，。·：！￥……（）+｛｝【】“”、|《》]|(?!\s)'\s+|\s+'(?!\s))''',
#                flags=re.UNICODE|re.DOTALL|re.VERBOSE)
punct_en = u'\[\]\,?"+_*\/\\&\$#^@!%~`<>:;\{\}'  # \(, \), - and . are excluded
punct_zh = u'．＂＃＄％＆＇＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏！？｡。'  # （, ） are excluded
punctuation = re.compile(ur'[' + punct_en + punct_zh + ']+',
                         flags=re.UNICODE | re.DOTALL | re.VERBOSE)

dot = re.compile(ur'[\.\-](?!\d+)|(?<=\W)[\.\-]',
                 flags=re.UNICODE | re.DOTALL | re.VERBOSE)
space = re.compile(ur'''\s+''',
                   flags=re.UNICODE | re.DOTALL | re.VERBOSE)


def clean_and_split(content):
    content = html_special.sub(ur' ', content)
    content = html_tag.sub(ur' ', content)
    content = punctuation.sub(ur' ', content)
    content = dot.sub(u' ', content)
    content = space.sub(u' ', content)

    return content.split()


par_pattern = ur'(?<={0})[^{0}{1}]{2}(?={1})'
par_symbols = [(ur'\(', u'\)', u'{1,3}'),
               (ur'（', ur'）', u'{1,3}')]
pars = [re.compile(par_pattern.format(*symbol)) for symbol in par_symbols]


def fix_table(source):
    # print '='*20
    # print type(source)
    nodes = lxml.html.fragments_fromstring(source)
    # print type(nodes)
    for node in nodes:
        tables = node.xpath('.//table')
        for table in tables:
            rows = table.xpath('.//tr')
            if rows:
                for row in rows:
                    cols = row.xpath('./td|th')
                    for col in cols:
                        # if not nasted table
                        if not col.xpath('.//table'):
                            # text = u''.join(list(col.itertext()))
                            text = u''.join([t.strip() for t in col.itertext()])
                            col.clear()
                            col.text = text.strip()

                cols = rows[0].xpath('./td|th')
                exts = [u''] * len(cols)
                for idx, col in enumerate(cols):
                    text = col.text
                    if not text:
                        text = ""
                    match = []
                    for par in pars:
                        match.extend(par.findall(text))
                    if match:
                        exts[idx] = match[-1]
                    elif text in (u'金额', u'中标金额', u'成交金额'):
                        exts[idx] = u'元'

                # logger.debug(u'find extension in table: '+' '.join(exts))
                # print u'find extension in table: '+' '.join(exts)
                for row in rows[1:]:
                    cols = row.xpath('./td|th')
                    for col, ext in zip(cols, exts):
                        if ext and not col.text.endswith(ext):
                            col.text += ext
                            # logger.debug(u'update table: {}'.format(col.text))
                            # print u'update table: {}'.format(col.text)
    source = u' '.join([lxml.etree.tostring(node, pretty_print=True) for node in nodes])
    # print '='*20
    # print source
    # print '='*20
    return source


com_num = re.compile(ur'[,，](\d{3})')


# html_span = re.compile(ur'[\s]*<(span|a)\b[^>]*>(.*?)</\1>[\s]*',flags=re.UNICODE|re.DOTALL|re.VERBOSE|re.M)
def clean_up(source):
    source = html_special.sub(u' ', source)
    source = re.sub(r'[rR][mM][bB]', u'¥', source)
    # source = html_span.sub(ur'\2', source)
    source = com_num.sub(ur'\1', source)
    # source = fix_table(source)
    return source


# parse the source and segment it into paragraphs according to html tags
# also clear out any useless html tags
# return a list of paragraphs (strings)
def paragraph(source):
    source = copy.copy(source)
    source = clean_up(source)

    nodes = lxml.html.fragments_fromstring(source)

    texts = []
    for node in nodes:
        for text in node.itertext():
            text = text.strip()
            if text:
                texts.append(text)
    return texts


# parse the paragraph and segment it into tokens according to punctuation
# return a list of tokens (strings)
par_pattern = ur'(?:{0})([^{0}{1}]{2})(?:{1})'
par_symbols = [(ur'\(', ur'\)', ur'{4,}'),
               (ur'（', ur'）', ur'{4,}')]
par_no_comp_list = [re.compile(par_pattern.format(*symbol)) for symbol in par_symbols]


def token(paragraph):
    content = copy.copy(paragraph)
    content = html_special.sub(u' ', content)
    content = html_tag.sub(u' ', content)
    content = punctuation.sub(u' ', content)
    for par in par_no_comp_list:
        content = par.sub(ur' \1 ', content)
    content = dot.sub(u' ', content)
    content = space.sub(u' ', content)

    return content.split()


# shortcut for above two
def paratokens(source):
    return [token(text) for text in paragraph(source)]
