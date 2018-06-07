# coding=utf-8
# author="Jianghua Zhao"


import bs4
import re
# from scpy.xawesome_crawler import BaseCrawler
# from collections import OrderedDict


def test():
    cities = OrderedDict()

    crawler = BaseCrawler()
    url = "http://data.acmr.com.cn/member/city/city_md.asp"
    html = crawler.get(url)
    bs = bs4.BeautifulSoup(html)
    blocks = bs.find_all("table", attrs={"class": "maintext"})
    blocks = blocks[8:]
    for block in blocks:
        trs = block.find_all("tr")
        prov = trs[0].find("a").get_text().strip()
        if prov.endswith(u"市"):
            cities[prov] = ""
        for i in range(2, len(trs)):
            tds = trs[i].find_all("td")
            for td in tds:
                city = td.get_text().strip()
                city = city.replace(prov, "")
                if city not in [u"县级市", u"[TOP]"] and len(city) > 0:
                    if city not in cities:
                        cities[city] = ""

    cities = [k[0] for k in cities.items()]
    with open("city.txt", "w") as f:
        f.write("\n".join(cities) + "\n")


def test_1():
    cities = OrderedDict()

    crawler = BaseCrawler()
    url = "http://data.acmr.com.cn/member/city/city_md.asp"
    html = crawler.get(url)
    bs = bs4.BeautifulSoup(html)
    blocks = bs.find_all("table", attrs={"class": "maintext"})
    blocks = blocks[8:]
    for block in blocks:
        trs = block.find_all("tr")
        prov = trs[0].find("a").get_text().strip()
        if not prov.endswith(u"市"):
            cities[prov] = ""

    cities = [k[0] for k in cities.items()]
    with open("prov.txt", "w") as f:
        f.write("\n".join(cities) + "\n")


if __name__ == "__main__":
    r = re.findall(u"[^，；。？！,;?!>]+", u'一、>>一、项目名称>>山西省太原市区2015-2016年党政机关会议定点场所采购项目')
    t = re.split(u"(?<=[\u4e00-\u9fa5]):", u"项目编号:ab45678 2009-12-26 12:12:12")
    print '|'.join(r)
    print '|'.join(t)
    # test_1()
