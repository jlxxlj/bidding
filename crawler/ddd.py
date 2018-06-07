# -*- encoding:utf-8 -*-



import re

__url_parser_table = []


def url_filter(url, *args):
    re_keyword = "\\.-?()"
    for item in re_keyword:
        url = url.replace(item, "\\" + item)
    url = url % args
    return url


def __uniform_html_code(html):
    try:
        if re.search('<meta.*?charset\=["]?(?:gb2312|gbk).*?>', html.lower()):
            html = html.decode(encoding="gbk")
        elif re.search('<meta.*?charset\=["]?utf-8.*?>', html.lower()):
            html = html.decode(encoding="utf-8")
    except:
        pass
    return html


def add_url(url):
    def decorator(function):
        def fun(html, pre_information):
            html = __uniform_html_code(html)
            return function(html, pre_information)

        __url_parser_table.append((url, fun))
        return fun

    return decorator


@add_url(url_filter("http://www.nxggzyjy.org/ningxiaweb/002"))
@add_url(url_filter("http://www.nxzfcg.gov.cn/ningxia/WebbuilderMIS/RedirectPage/RedirectPage.jspx"))
def nx_ggzyjyzx_nr(html, pre_information):
    links = 123
    contents = '123'
    return links, contents

if __name__ == '__main__':
    print __url_parser_table[0][0]