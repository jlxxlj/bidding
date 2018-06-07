# coding=utf-8
# author="Jianghua Zhao"

from util import *
import hashlib
import json

start_urls = []


def add_start(start):
    string = json.dumps(start, sort_keys=True)
    uid = hashlib.sha1(string).hexdigest()
    start[UNI_ORIGIN_ID] = uid
    start_urls.append(start)


# 台湾

# 澳门

# 香港

# 宁夏
add_start({ORIGIN_REGION: u"宁夏",
           URL: "http://www.nxzfcg.gov.cn/ningxia/services/BulletinWebServer/getInfoListInAbout?response=application/json&pageIndex=1&pageSize=18&siteguid=2e221293-d4a1-40ed-854b-dcfea12e61c5&categorynum=002001003&cityname=&title=",
           ANNOUNCE_TYPE: u"中标公示/公告",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"宁夏回族自治区公共资源交易网",
           NOTE: u"宁夏回族自治区公共资源交易网-工程建设"})
add_start({ORIGIN_REGION: u"宁夏",
           URL: "http://www.nxzfcg.gov.cn/ningxia/services/BulletinWebServer/getInfoListInAbout?response=application/json&pageIndex=1&pageSize=18&siteguid=2e221293-d4a1-40ed-854b-dcfea12e61c5&categorynum=002002003&cityname=&title=",
           ANNOUNCE_TYPE: u"中标/成交公示",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"宁夏回族自治区公共资源交易网",
           NOTE: u"宁夏回族自治区公共资源交易网-政府采购"})

# 广西
# 广西壮族自治区政府采购网
add_start({ORIGIN_REGION: u"广西",
           URL: "http://www.gxzfcg.gov.cn/CmsNewsController/getCmsNewsList/channelCode-shengji_zbgg/param_bulletin/20/page_1.html",
           ANNOUNCE_TYPE: u"中标公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"广西壮族自治区政府采购网",
           NOTE: u"广西壮族自治区政府采购网-区本级采购"})
add_start({ORIGIN_REGION: u"广西",
           URL: "http://www.gxzfcg.gov.cn/CmsNewsController/getCmsNewsList/channelCode-shengji_cjgg/param_bulletin/20/page_1.html",
           ANNOUNCE_TYPE: u"成交公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"广西壮族自治区政府采购网",
           NOTE: u"广西壮族自治区政府采购网-区本级采购"})
add_start({ORIGIN_REGION: u"广西",
           URL: "http://www.gxzfcg.gov.cn/CmsNewsController/getCmsNewsList/channelCode-sxjcg_zbgg/param_bulletin/20/page_1.html",
           ANNOUNCE_TYPE: u"中标公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"广西壮族自治区政府采购网",
           NOTE: u"广西壮族自治区政府采购网-市(县)级采购"})
add_start({ORIGIN_REGION: u"广西",
           URL: "http://www.gxzfcg.gov.cn/CmsNewsController/getCmsNewsList/channelCode-sxjcg_cjgg/param_bulletin/20/page_1.html",
           ANNOUNCE_TYPE: u"成交公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"广西壮族自治区政府采购网",
           NOTE: u"广西壮族自治区政府采购网-市(县)级采购"})
# 广西壮族自治区政府采购中心
add_start({ORIGIN_REGION: u"广西",
           URL: "http://www.gxgp.gov.cn/zbgkzb/index.htm",
           ANNOUNCE_TYPE: u"中标公告",
           PURCHASE_TYPE: u"公开招标",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"广西壮族自治区政府采购中心",
           NOTE: u"广西壮族自治区政府采购中心-公开招标"})
add_start({ORIGIN_REGION: u"广西",
           URL: "http://www.gxgp.gov.cn/zbjz/index.htm",
           ANNOUNCE_TYPE: u"中标公告",
           PURCHASE_TYPE: u"竞争性谈判",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"广西壮族自治区政府采购中心",
           NOTE: u"广西壮族自治区政府采购中心-竞争性谈判"})
add_start({ORIGIN_REGION: u"广西",
           URL: "http://www.gxgp.gov.cn/zbdyly/index.htm",
           ANNOUNCE_TYPE: u"中标公告",
           PURCHASE_TYPE: u"单一来源采购",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"广西壮族自治区政府采购中心",
           NOTE: u"广西壮族自治区政府采购中心-单一来源采购"})
add_start({ORIGIN_REGION: u"广西",
           URL: "http://www.gxgp.gov.cn/zbxjcg/index.htm",
           ANNOUNCE_TYPE: u"中标公告",
           PURCHASE_TYPE: u"询价采购",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"广西壮族自治区政府采购中心",
           NOTE: u"广西壮族自治区政府采购中心-询价采购"})

# 西藏
# 西藏自治区招标投标网
add_start({ORIGIN_REGION: u"西藏",
           URL: "http://www.xzzbtb.gov.cn/xz/publish-notice!preAwardNoticeView.do?PAGE=1",
           ANNOUNCE_TYPE: u"中标公告",
           SLEEP_SECOND: 2,
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"西藏自治区招标投标网",
           NOTE: u"西藏自治区招标投标网-中标公告"})

# 新疆
# 新疆维吾尔自治区政府采购网
add_start({ORIGIN_REGION: u"新疆",
           URL: "http://zfcg.xjcz.gov.cn/djl/cmsPublishAction.do?method=selectCmsInfoPublishList&channelId=16",
           ANNOUNCE_TYPE: u"中标公告",
           METHOD: POST,
           PARAMS: {"pagecount": 1, "channelId": 16},
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"新疆维吾尔自治区政府采购网",
           NOTE: u"新疆维吾尔自治区政府采购网-中标公告"})

# 内蒙古
# 内蒙古自治区公共资源交易网
# TODO post传递的参数不起作用
add_start({ORIGIN_REGION: u"内蒙古",
           URL: "http://www.nmgzfcg.gov.cn/jyxx/jsgcZbjggs=======",
           PROJECT_TYPE: u"工程建设",
           ANNOUNCE_TYPE: u"中标公告",
           NOTE: u"内蒙古自治区公共资源交易网-工程建设-中标公告"})
add_start({ORIGIN_REGION: u"内蒙古",
           URL: "http://www.nmgzfcg.gov.cn/jyxx/zfcg/zbjggs=======",
           PROJECT_TYPE: u"政府采购",
           ANNOUNCE_TYPE: u"中标结果公告",
           NOTE: u"内蒙古自治区公共资源交易网-政府采购-中标结果公告"})

# 内蒙古自治区政府采购网
add_start({ORIGIN_REGION: u"内蒙古",
           URL: "http://www.nmgp.gov.cn/procurement/pages/tender.jsp?type=2&pos=1",
           ANNOUNCE_TYPE: u"中标成交公示",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"内蒙古自治区政府采购网",
           NOTE: u"内蒙古自治区政府采购网-自治区采购公告-中标成交公示"})

# 海南
# 中国海南政府采购网
add_start({ORIGIN_REGION: u"海南",
           URL: "http://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?currentPage=1&begindate=&enddate=&title=&bid_type=108&proj_number=&zone=",
           ANNOUNCE_TYPE: u"中标公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"中国海南政府采购网",
           NOTE: u"中国海南政府采购网-2016年6月6日后数据"})
add_start({ORIGIN_REGION: u"海南",
           URL: "http://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?currentPage=1&begindate=&enddate=&title=&bid_type=112&proj_number=&zone=",
           ANNOUNCE_TYPE: u"成交公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"中国海南政府采购网",
           NOTE: u"中国海南政府采购网-2016年6月6日后数据"})
add_start({ORIGIN_REGION: u"海南",
           URL: "http://www.hainan.gov.cn/was5/search/rollnews.jsp?searchword=&siteid=cjgg&type=&lmmc=2&page=1",
           ANNOUNCE_TYPE: u"成交公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"中国海南政府采购网",
           NOTE: u"中国海南政府采购网-2016年6月6日前历史数据"})

# 广东
# 广东省政府采购网
add_start({ORIGIN_REGION: u"广东",
           URL: "http://www.gdgpo.gov.cn/queryMoreInfoList.do",
           ANNOUNCE_TYPE: u"中标公告",
           METHOD: POST,
           PARAMS: {"channelCode": "0008",
                    "sitewebId": -1,
                    "pageIndex": 1,
                    "pageSize": 15,
                    "pointPageIndexId": 0},
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"广东省政府采购网",
           NOTE: u"广东省政府采购网-中标公告"})
# 广东阳江公共资源交易中心
add_start({ORIGIN_REGION: u"广东",
           URL: "http://www.yjggzy.cn/Query/ArticleQuery2/43a0fbd899a34465945625ea39e34d9c?page=1",
           REGION: u"广东>>阳江市",
           ANNOUNCE_TYPE: u"结果公示",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"广东阳江公共资源交易中心",
           NOTE: u"广东阳江公共资源交易中心-结果公示-政府采购"})
add_start({ORIGIN_REGION: u"广东",
           URL: "http://www.yjggzy.cn/Query/JsgcWinBidAfficheQuery2/46eb01f656f4468cb65a434b77d73065?page=1",
           REGION: u"广东>>阳江市",
           ANNOUNCE_TYPE: u"结果公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"广东阳江公共资源交易中心",
           NOTE: u"广东阳江公共资源交易中心-结果公示-工程建设"})
add_start({ORIGIN_REGION: u"广东",
           URL: "http://www.yjggzy.cn/Query/OnResultsQuery2/4a7740eadb8442af9551896106dedf51?page=1",
           REGION: u"广东>>阳江市",
           ANNOUNCE_TYPE: u"结果公示",
           PROJECT_TYPE: u"土地与矿业权交易",
           WEBSITE: u"广东阳江公共资源交易中心",
           NOTE: u"广东阳江公共资源交易中心-结果公示-土地与矿业权交易"})
add_start({ORIGIN_REGION: u"广东",
           URL: "http://www.yjggzy.cn/Query/CqjyQuery2/b14fe81f79a5493a95e7ef973704aff7?page=1",
           REGION: u"广东>>阳江市",
           ANNOUNCE_TYPE: u"结果公示",
           PROJECT_TYPE: u"产权交易",
           WEBSITE: u"广东阳江公共资源交易中心",
           NOTE: u"广东阳江公共资源交易中心-结果公示-产权交易"})

# 云南
# 云南政府采购网
add_start({ORIGIN_REGION: u"云南",
           URL: "http://www.yngp.com/bulletin.do?method=moreListQuery",
           METHOD: POST,
           PARAMS: {
               "current": 1,
               "rowCount": 50,
               "searchPhrase": "",
               "sign": 2,
               "query_bulletintitle": "",
               "query_startTime": "",
               "query_endTime": "",
               "query_sign": 1,
               "flag": 1,
               "listSign": 1,
               "districtCode": "all",
           },
           ANNOUNCE_TYPE: u"采购结果公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"云南政府采购网",
           NOTE: u"云南省政府采购网-采购结果公告"})

# 贵州
# 贵州省招标投标公共服务平台
typs = {u"工程建设": 1, u"政府采购": 2, u"土地矿产": 3, u"产权交易": 4, u"药品采购": 5}
for typ, code in typs.items():
    add_start({ORIGIN_REGION: u"贵州",
               URL: "http://www.gzzbw.cn/searchCustom.jspx?noticeType1=%s&noticeType2=&noticeType3=&name=&startTime=&endTime=&tpl=zbgs" % (
                   code),
               ANNOUNCE_TYPE: u"中标公示",
               PROJECT_TYPE: typ,
               WEBSITE: u"贵州省招标投标公共服务平台",
               NOTE: u"贵州省招标投标公共服务平台-中标公示"})

# 青海
# 青海省政府采购
add_start({ORIGIN_REGION: u"青海",
           URL: "http://www.ccgp-qinghai.gov.cn/jilin/zbxxController.form?declarationType=W&type=1&pageNo=0",
           ANNOUNCE_TYPE: u"中标公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"青海省政府采购",
           NOTE: u"青海省政府采购网-省级公告信息-中标公告"})
add_start({ORIGIN_REGION: u"青海",
           URL: "http://www.ccgp-qinghai.gov.cn/jilin/zbxxController.form?declarationType=W&type=2&pageNo=0",
           ANNOUNCE_TYPE: u"中标公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"青海省政府采购",
           NOTE: u"青海省政府采购网-州市县公告信息-中标公告"})

# 甘肃
# 甘肃政府采购网
add_start({ORIGIN_REGION: u"甘肃",
           URL: "http://www.gszfcg.gansu.gov.cn/web/doSearch.action?op=%271%27&articleSearchInfoVo.classname=12802&articleSearchInfoVo.tflag=1",
           ANNOUNCE_TYPE: u"中标公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"甘肃政府采购网",
           NOTE: u"甘肃政府采购网-中标公告"})
add_start({ORIGIN_REGION: u"甘肃",
           URL: "http://www.gszfcg.gansu.gov.cn/web/doSearch.action?op=%271%27&articleSearchInfoVo.classname=12804&articleSearchInfoVo.tflag=1",
           ANNOUNCE_TYPE: u"成交公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"甘肃政府采购网",
           NOTE: u"甘肃政府采购网-成交公告"})

# 四川
# 四川政府采购
add_start({ORIGIN_REGION: u"四川",
           URL: "http://www.sczfcg.com/CmsNewsController.do?method=recommendBulletinList&rp=25&page=1&moreType=provincebuyBulletinMore&channelCode=jggg",
           ANNOUNCE_TYPE: u"结果公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"四川政府采购",
           NOTE: u"四川政府采购网-省结果公告列表"})
add_start({ORIGIN_REGION: u"四川",
           URL: "http://www.sczfcg.com/CmsNewsController.do?method=recommendBulletinList&rp=25&page=1&moreType=provincebuyBulletinMore&channelCode=shiji_jggg",
           ANNOUNCE_TYPE: u"成交公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"四川政府采购",
           NOTE: u"四川政府采购网-市县结果公告列表"})

# TODO
# 江西
# 江西省公共资源交易网
for i in range(10):
    add_start({ORIGIN_REGION: u"江西",
               URL: "http://ggzy.jiangxi.gov.cn/jxzbw/jyxx/002001/002001005/",
               NOTE: u"初始化与服务器的链接"})
# add_start({ORIGIN_REGION: u"江西",
#            URL: "http://ggzy.jiangxi.gov.cn/jxzbw/zfcg/017002/017002004/MoreInfo.aspx?CategoryNum=017002004",
#            PROJECT_TYPE: u"政府采购",
#            ANNOUNCE_TYPE: u"中标公告",
#            WEBSITE: u"江西省公共资源交易网",
#            NOTE: u"江西省公共资源交易网-中标公告"})
add_start({ORIGIN_REGION: u"江西",
           URL: "http://ggzy.jiangxi.gov.cn/jxzbw/jyxx/002004/002004004/MoreInfo.aspx?CategoryNum=002004004",
           PROJECT_TYPE: u"政府采购",
           ANNOUNCE_TYPE: u"结果公示",
           WEBSITE: u"江西省公共资源交易网",
           NOTE: u"江西省公共资源交易网-结果公示"})
add_start({ORIGIN_REGION: u"江西",
           URL: "http://ggzy.jiangxi.gov.cn/jxzbw/jyxx/002010/002010004/MoreInfo.aspx?CategoryNum=002010004",
           PROJECT_TYPE: u"重点工程",
           ANNOUNCE_TYPE: u"结果公示",
           WEBSITE: u"江西省公共资源交易网",
           NOTE: u"江西省公共资源交易网-结果公示"})
add_start({ORIGIN_REGION: u"江西",
           URL: "http://ggzy.jiangxi.gov.cn/jxzbw/jyxx/002008/002008002/MoreInfo.aspx?CategoryNum=002008002",
           PROJECT_TYPE: u"药品采购",
           ANNOUNCE_TYPE: u"结果公示",
           WEBSITE: u"江西省公共资源交易网",
           NOTE: u"江西省公共资源交易网-结果公示"})
add_start({ORIGIN_REGION: u"江西",
           URL: "http://ggzy.jiangxi.gov.cn/jxzbw/jyxx/002009/002009004/MoreInfo.aspx?CategoryNum=002009004",
           PROJECT_TYPE: u"铁路工程",
           ANNOUNCE_TYPE: u"结果公示",
           WEBSITE: u"江西省公共资源交易网",
           NOTE: u"江西省公共资源交易网-结果公示"})
add_start({ORIGIN_REGION: u"江西",
           URL: "http://ggzy.jiangxi.gov.cn/jxzbw/jyxx/002003/002003004/MoreInfo.aspx?CategoryNum=002003004",
           PROJECT_TYPE: u"水利工程",
           ANNOUNCE_TYPE: u"结果公示",
           WEBSITE: u"江西省公共资源交易网",
           NOTE: u"江西省公共资源交易网-结果公示"})
add_start({ORIGIN_REGION: u"江西",
           URL: "http://ggzy.jiangxi.gov.cn/jxzbw/jyxx/002002/002002005/MoreInfo.aspx?CategoryNum=002002005",
           PROJECT_TYPE: u"交通工程",
           ANNOUNCE_TYPE: u"结果公示",
           WEBSITE: u"江西省公共资源交易网",
           NOTE: u"江西省公共资源交易网-结果公示"})
add_start({ORIGIN_REGION: u"江西",
           URL: "http://ggzy.jiangxi.gov.cn/jxzbw/jyxx/002001/002001005/MoreInfo.aspx?CategoryNum=002001005",
           PROJECT_TYPE: u"房建及市政",
           ANNOUNCE_TYPE: u"结果公示",
           WEBSITE: u"江西省公共资源交易网",
           NOTE: u"江西省公共资源交易网-结果公示"})

# 福建
# 福建省政府采购网
for _ in range(10):
    add_start({ORIGIN_REGION: u"福建",
               URL: "http://cz.fjzfcg.gov.cn/web/fjsindex/index.html"})

levels = ["city", "county"]
reg = ["jzcg", "fscg"]
for rg in reg:
    add_start({ORIGIN_REGION: u"福建",
               URL: "http://cz.fjzfcg.gov.cn/n/webfjs/queryPageData.do",
               METHOD: POST,
               PARAMS: {"page": 1,
                        "rows": 20,
                        "sid": "200100002",
                        "level": "province",
                        "zzxs": rg,
                        "cgfs": "zbcg"},
               ANNOUNCE_TYPE: u"中标公告",
               PROJECT_TYPE: u"政府采购",
               WEBSITE: u"福建省政府采购网",
               NOTE: u"福建省政府采购网-中标公告-省级"})
for level in levels:
    add_start({ORIGIN_REGION: u"福建",
               URL: "http://cz.fjzfcg.gov.cn/n/webfjs/queryPageData.do",
               METHOD: POST,
               PARAMS: {"page": 1,
                        "rows": 20,
                        "sid": "200100002",
                        "level": level},
               ANNOUNCE_TYPE: u"中标公告",
               PROJECT_TYPE: u"政府采购",
               WEBSITE: u"福建省政府采购网",
               NOTE: u"福建省政府采购网-中标公告-市县级"})

# 安徽
# 安徽省政府采购网
add_start({ORIGIN_REGION: u"安徽",
           URL: "http://www.ccgp-anhui.gov.cn/mhxt/MhxtSearchBulletinController.zc?method=bulletinChannelRightDown",
           METHOD: POST,
           PARAMS: {"pageNo": 1,
                    "pageSize": 15,
                    "channelCode": "sjcg",
                    "bType": "03"},
           ANNOUNCE_TYPE: u"中标公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"安徽省政府采购网",
           NOTE: u"安徽省政府采购网-中标公告"})
add_start({ORIGIN_REGION: u"安徽",
           URL: "http://www.ccgp-anhui.gov.cn/mhxt/MhxtSearchBulletinController.zc?method=bulletinChannelRightDown",
           METHOD: POST,
           PARAMS: {"pageNo": 1,
                    "pageSize": 15,
                    "channelCode": "sjcg",
                    "bType": "04"},
           ANNOUNCE_TYPE: u"成交公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"安徽省政府采购网",
           NOTE: u"安徽省政府采购网-成交公告"})

# 浙江
# 浙江政府采购网
add_start({ORIGIN_REGION: u"浙江",
           URL: "http://www.zjzfcg.gov.cn/new/articleSearch/search_1.do?count=30&bidType=&region=&chnlIds=208,212&bidMenu=&searchKey=&bidWay=&applyYear=2017&flag=1&releaseStartDate=&noticeEndDate=&releaseEndDate=&noticeEndDate1=&zjzfcg=0",
           ANNOUNCE_TYPE: u"中标成交公示",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"浙江政府采购网",
           NOTE: u"浙江政府采购网-中标成交公示"})
add_start({ORIGIN_REGION: u"浙江",
           URL: "http://www.zjzfcg.gov.cn/new/articleSearch/search_1.do?count=30&bidType=&region=&chnlIds=209,213&bidMenu=&searchKey=&bidWay=&applyYear=2017&flag=1&releaseStartDate=&noticeEndDate=&releaseEndDate=&noticeEndDate1=&zjzfcg=0",
           ANNOUNCE_TYPE: u"中标成交公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"浙江政府采购网",
           NOTE: u"浙江政府采购网-中标成交公告"})

# 江苏
# 江苏政府采购网
add_start({ORIGIN_REGION: u"江苏",
           URL: "http://www.ccgp-jiangsu.gov.cn/pub/jszfcg/cgxx/cjgg/index.html",
           ANNOUNCE_TYPE: u"成交公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"江苏政府采购网",
           NOTE: u"江苏政府采购网-成交公告"})

# 吉林
# 吉林省公共资源交易信息网
add_start({ORIGIN_REGION: u"吉林",
           URL: "http://ggzyjy.jl.gov.cn/JiLinZtb//Template/Default/MoreInfoJYXX.aspx?CategoryNum=004002",
           ANNOUNCE_TYPE: u"预中标公示",
           MAX_CRAWLER_NUMBER: 1,
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"吉林省公共资源交易信息网",
           NOTE: u"吉林省公共资源交易信息网-预中标公示"})

# 辽宁
# 辽宁省政府集中采购网
add_start({ORIGIN_REGION: u"辽宁",
           URL: "http://www.lnzc.gov.cn/SitePages/AfficheListAll2.aspx",
           METHOD: POST,
           PARAMS: {
               "__EVENTTARGET": "ctl00$ctl00$ContentPlaceHolderMain$ContentPlaceHolderMain$g_8ac3be76_5de3_4bbf_a034_d924bd6995c5",
               "__EVENTARGUMENT": "dvt_firstrow={1};dvt_startposition={}",
               "__REQUESTDIGEST": "0x50727C2A11FCF46E6F759B85E7D027EC1A2759A18DE2B22BAF56BF88DE4596CE248C6F71A0B2602BC37B31A76E1B1533F4FD8E1134573FB30B44E7DFF8047B8C,05 Dec 2016 09:34:38 -0000",
               "__VIEWSTATE": "/wEPBSpWU0tleTozMGJjODdkMy1hNTE3LTQzODktODY5Zi02ZGQ3MzIwZmIwODVkwu1CoWgCUJUVXx0iBZk60pbGrV5zsS62p5R3FPc+Y+o="
           },
           ANNOUNCE_TYPE: u"中标公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"辽宁省政府集中采购网",
           NOTE: u"辽宁省政府集中采购网-中标公告"})

# 黑龙江
# 黑龙江省政府采购网
# TODO
for i in range(10):
    add_start({ORIGIN_REGION: u"黑龙江",
               URL: "http://www.hljcg.gov.cn/xwzs!index.action",
               NOTE: u"初始化与服务器的链接"})
add_start({ORIGIN_REGION: u"黑龙江",
           URL: "http://www.hljcg.gov.cn/xwzs!queryXwxxqx.action",
           # MAX_CRAWLER_NUMBER: 1,
           ANNOUNCE_TYPE: u"成交公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"黑龙江省政府采购网",
           NOTE: u"黑龙江省政府采购网-成交公告"})

# 湖南
# 湖南省政府采购网
add_start({ORIGIN_REGION: u"湖南",
           URL: "http://www.ccgp-hunan.gov.cn/mvc/getNoticeList4Web.do",
           METHOD: POST,
           PARAMS: {"nType": "dealNotices",
                    "page": 1,
                    "pageSize": 18},
           SLEEP_SECOND: 1,
           ANNOUNCE_TYPE: u"成交公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"湖南省政府采购网",
           NOTE: u"湖南省政府采购网-成交公告"})
add_start({ORIGIN_REGION: u"湖南",
           URL: "http://www.ccgp-hunan.gov.cn/mvc/getNoticeListOfCityCounty.do",
           METHOD: POST,
           PARAMS: {"nType": "dealNotices",
                    "page": 1,
                    "pageSize": 18},
           SLEEP_SECOND: 1,
           ANNOUNCE_TYPE: u"成交公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"湖南省政府采购网",
           NOTE: u"湖南省政府采购网-成交公告"})

# 湖北
# 湖北招标网
add_start({ORIGIN_REGION: u"湖北",
           URL: "http://www.hbzbw.com/zhongbiao.asp?page=1&keywords=&dq=&classname=%B9%A4%B3%CC%D5%D0%B1%EA",
           ANNOUNCE_TYPE: u"中标公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"湖北招标网",
           NOTE: u"湖北招标网-中标公告"})

# 陕西
# 陕西招标信息网
add_start({ORIGIN_REGION: u"陕西",
           URL: "http://www.sxzhaobiao.com/zhongbiao.asp?page=1&keywords=&dq=&classname=%B9%A4%B3%CC%D5%D0%B1%EA",
           ANNOUNCE_TYPE: u"中标公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"陕西招标信息网",
           NOTE: u"陕西招标信息网-中标公告"})

# 山东
# 山东招标采购网
add_start({ORIGIN_REGION: u"山东",
           URL: "http://www.sdzbcg.com/zhongbiao.asp?page=1&keywords=&dq=",
           ANNOUNCE_TYPE: u"中标公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"山东招标采购网",
           NOTE: u"山东招标采购网-中标公告"})

# 山西
add_start({ORIGIN_REGION: u"山西",
           URL: "http://www.ccgp-shanxi.gov.cn/view.php?nav=104",
           ANNOUNCE_TYPE: u"结果公告",
           SLEEP_SECOND: 60,
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"中国山西政府采购网",
           NOTE: u"中国山西政府采购网-结果公告"})

# 河南
# 河南招标信息网
add_start({ORIGIN_REGION: u"河南",
           URL: "http://www.hnzhaobiao.com/zhongbiao.asp?page=1&bigclassname=%D6%D0%B1%EA%B9%AB%B8%E6&smallclassname=%D6%D0%B1%EA%B9%AB%B8%E6&keywords=&dq=",
           ANNOUNCE_TYPE: u"中标公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"河南招标信息网",
           NOTE: u"河南招标信息网-中标公告"})

# 河北
# # 河北省招标投标综合网
# add_start({ORIGIN_REGION: u"河北",
#            URL: "http://www.hebeibidding.com.cn/STender/More.aspx",
#            METHOD: POST,
#            PARAMS: {"Ddl_PageNumber": 1},
#            ANNOUNCE_TYPE: u"中标公告",
#            NOTE: u"河北省招标投标综合网-中标公告"})

# # 河北省省级政府采购中心
# add_start({ORIGIN_REGION: u"河北",
#            URL: "http://www.hbgp.gov.cn/046/1.html",
#            ANNOUNCE_TYPE: u"结果公告",
#            NOTE: u"河北省省级政府采购中心-结果公告"})

# # 河北省公共资源交易中心
# add_start({ORIGIN_REGION: u"河北",
#            URL: "http://www.hebggzy.cn/002/002009/002009001/002009001006/1.html",
#            ANNOUNCE_TYPE: u"结果公告",
#            PROJECT_TYPE: u"政府采购",
#            WEBSITE: u"河北省公共资源交易中心",
#            NOTE: u"河北省公共资源交易中心-结果公告-政府采购"})
# add_start({ORIGIN_REGION: u"河北",
#            URL: "http://www.hebggzy.cn/002/002009/002009002/002009002003/1.html",
#            ANNOUNCE_TYPE: u"中标候选人公示",
#            PROJECT_TYPE: u"工程建设",
#            WEBSITE: u"河北省公共资源交易中心",
#            NOTE: u"河北省公共资源交易中心-中标候选人公示-工程建设"})

# 河北省公共资源交易服务平台
add_start({ORIGIN_REGION: u"河北",
           URL: "http://www.hebpr.cn/002/002009/002009001/002009001005/1.html",
           ANNOUNCE_TYPE: u"中标候选公示",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"河北省公共资源交易服务平台",
           NOTE: u"河北省公共资源交易服务平台-中标候选公示-政府采购"})
add_start({ORIGIN_REGION: u"河北",
           URL: "http://www.hebpr.cn/002/002009/002009001/002009001006/1.html",
           ANNOUNCE_TYPE: u"结果公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"河北省公共资源交易服务平台",
           NOTE: u"河北省公共资源交易服务平台-中标候选公示-政府采购"})
add_start({ORIGIN_REGION: u"河北",
           URL: "http://www.hebpr.cn/002/002009/002009002/002009002003/1.html",
           ANNOUNCE_TYPE: u"中标候选人公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"河北省公共资源交易服务平台",
           NOTE: u"河北省公共资源交易服务平台-中标候选人公示-工程建设"})
add_start({ORIGIN_REGION: u"河北",
           URL: "http://www.hebpr.cn/002/002009/002009002/002009002005/1.html",
           ANNOUNCE_TYPE: u"中标结果公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"河北省公共资源交易服务平台",
           NOTE: u"河北省公共资源交易服务平台-中标结果公示-工程建设"})

# 河北省政府采购网
hb_region_code = [
    [u"河北>>石家庄市>>长安区", "130000000-130100000-130102000"],
    [u"河北>>石家庄市>>桥东区", "130000000-130100000-130103000"],
    [u"河北>>石家庄市>>桥西区", "130000000-130100000-130104000"],
    [u"河北>>石家庄市>>新华区", "130000000-130100000-130105000"],
    [u"河北>>石家庄市>>裕华区", "130000000-130100000-130106000"],
    [u"河北>>石家庄市>>矿区", "130000000-130100000-130107000"],
    [u"河北>>石家庄市>>正定新区", "130000000-130100000-130186000"],
    [u"河北>>石家庄市>>高新区", "130000000-130100000-130111000"],
    [u"河北>>石家庄市>>井陉县", "130000000-130100000-130121000"],
    [u"河北>>石家庄市>>正定县", "130000000-130100000-130123000"],
    [u"河北>>石家庄市>>栾城县", "130000000-130100000-130124000"],
    [u"河北>>石家庄市>>行唐县", "130000000-130100000-130125000"],
    [u"河北>>石家庄市>>灵寿县", "130000000-130100000-130126000"],
    [u"河北>>石家庄市>>高邑县", "130000000-130100000-130127000"],
    [u"河北>>石家庄市>>深泽县", "130000000-130100000-130128000"],
    [u"河北>>石家庄市>>赞皇县", "130000000-130100000-130129000"],
    [u"河北>>石家庄市>>无极县", "130000000-130100000-130130000"],
    [u"河北>>石家庄市>>平山县", "130000000-130100000-130131000"],
    [u"河北>>石家庄市>>元氏县", "130000000-130100000-130132000"],
    [u"河北>>石家庄市>>赵县", "130000000-130100000-130133000"],
    [u"河北>>石家庄市>>藁城市", "130000000-130100000-130182000"],
    [u"河北>>石家庄市>>晋州市", "130000000-130100000-130183000"],
    [u"河北>>石家庄市>>新乐市", "130000000-130100000-130184000"],
    [u"河北>>石家庄市>>鹿泉市", "130000000-130100000-130185000"],
    [u"河北>>石家庄市>>循环化工业园区", "130000000-130100000-130187000"],
    [u"河北>>石家庄市", "130000000-130100000"],
    [u"河北>>辛集市", "130000000-130181000"],
    [u"河北>>唐山市>>路南区", "130000000-130200000-130202000"],
    [u"河北>>唐山市>>路北区", "130000000-130200000-130203000"],
    [u"河北>>唐山市>>古冶区", "130000000-130200000-130204000"],
    [u"河北>>唐山市>>开平区", "130000000-130200000-130205000"],
    [u"河北>>唐山市>>丰润区", "130000000-130200000-130208000"],
    [u"河北>>唐山市>>高新技术开发区区", "130000000-130200000-130211000"],
    [u"河北>>唐山市>>海港开发区", "130000000-130200000-130212000"],
    [u"河北>>唐山市>>南堡开发区", "130000000-130200000-130213000"],
    [u"河北>>唐山市>>芦台开发区", "130000000-130200000-130214000"],
    [u"河北>>唐山市>>汉沽管理区", "130000000-130200000-130215000"],
    [u"河北>>唐山市>>曹妃甸区", "130000000-130200000-130209000"],
    [u"河北>>唐山市>>滦县", "130000000-130200000-130223000"],
    [u"河北>>唐山市>>滦南县", "130000000-130200000-130224000"],
    [u"河北>>唐山市>>乐亭县", "130000000-130200000-130225000"],
    [u"河北>>唐山市>>迁西县", "130000000-130200000-130227000"],
    [u"河北>>唐山市>>玉田县", "130000000-130200000-130229000"],
    [u"河北>>唐山市>>唐海县", "130000000-130200000-130230000"],
    [u"河北>>唐山市>>遵化市", "130000000-130200000-130281000"],
    [u"河北>>唐山市>>丰南市", "130000000-130200000-130207000"],
    [u"河北>>唐山市>>迁安市", "130000000-130200000-130283000"],
    [u"河北>>唐山市", "130000000-130200000"],
    [u"河北>>秦皇岛市>>海港区", "130000000-130300000-130302000"],
    [u"河北>>秦皇岛市>>山海关区", "130000000-130300000-130303000"],
    [u"河北>>秦皇岛市>>北戴河区", "130000000-130300000-130304000"],
    [u"河北>>秦皇岛市>>开发区", "130000000-130300000-130311000"],
    [u"河北>>秦皇岛市>>北戴河新区", "130000000-130300000-130313000"],
    [u"河北>>秦皇岛市>>青龙县", "130000000-130300000-130321000"],
    [u"河北>>秦皇岛市>>昌黎县", "130000000-130300000-130322000"],
    [u"河北>>秦皇岛市>>抚宁县", "130000000-130300000-130323000"],
    [u"河北>>秦皇岛市>>卢龙县", "130000000-130300000-130324000"],
    [u"河北>>秦皇岛市", "130000000-130300000"],
    [u"河北>>邯郸市>>邯山区", "130000000-130400000-130402000"],
    [u"河北>>邯郸市>>丛台区", "130000000-130400000-130403000"],
    [u"河北>>邯郸市>>复兴区", "130000000-130400000-130404000"],
    [u"河北>>邯郸市>>峰峰矿区", "130000000-130400000-130406000"],
    [u"河北>>邯郸市>>开发区", "130000000-130400000-130411000"],
    [u"河北>>邯郸市>>马头生态工业城", "130000000-130400000-130412000"],
    [u"河北>>邯郸市>>邯郸县", "130000000-130400000-130421000"],
    [u"河北>>邯郸市>>临漳县", "130000000-130400000-130423000"],
    [u"河北>>邯郸市>>成安县", "130000000-130400000-130424000"],
    [u"河北>>邯郸市>>大名县", "130000000-130400000-130425000"],
    [u"河北>>邯郸市>>涉县", "130000000-130400000-130426000"],
    [u"河北>>邯郸市>>磁县", "130000000-130400000-130427000"],
    [u"河北>>邯郸市>>肥乡县", "130000000-130400000-130428000"],
    [u"河北>>邯郸市>>永年县", "130000000-130400000-130429000"],
    [u"河北>>邯郸市>>邱县", "130000000-130400000-130430000"],
    [u"河北>>邯郸市>>鸡泽县", "130000000-130400000-130431000"],
    [u"河北>>邯郸市>>广平县", "130000000-130400000-130432000"],
    [u"河北>>邯郸市>>馆陶县", "130000000-130400000-130433000"],
    [u"河北>>邯郸市>>魏县", "130000000-130400000-130434000"],
    [u"河北>>邯郸市>>曲周县", "130000000-130400000-130435000"],
    [u"河北>>邯郸市>>武安市", "130000000-130400000-130481000"],
    [u"河北>>邯郸市", "130000000-130400000"],
    [u"河北>>邢台市>>桥东区", "130000000-130500000-130502000"],
    [u"河北>>邢台市>>桥西区", "130000000-130500000-130503000"],
    [u"河北>>邢台市>>高新技术开区区", "130000000-130500000-130511000"],
    [u"河北>>邢台市>>大曹庄管理区", "130000000-130500000-130512000"],
    [u"河北>>邢台市>>邢台县", "130000000-130500000-130521000"],
    [u"河北>>邢台市>>临城县", "130000000-130500000-130522000"],
    [u"河北>>邢台市>>内邱县", "130000000-130500000-130523000"],
    [u"河北>>邢台市>>柏乡县", "130000000-130500000-130524000"],
    [u"河北>>邢台市>>隆尧县", "130000000-130500000-130525000"],
    [u"河北>>邢台市>>任县", "130000000-130500000-130526000"],
    [u"河北>>邢台市>>南和县", "130000000-130500000-130527000"],
    [u"河北>>邢台市>>宁晋县", "130000000-130500000-130528000"],
    [u"河北>>邢台市>>巨鹿县", "130000000-130500000-130529000"],
    [u"河北>>邢台市>>新河县", "130000000-130500000-130530000"],
    [u"河北>>邢台市>>广宗县", "130000000-130500000-130531000"],
    [u"河北>>邢台市>>平乡县", "130000000-130500000-130532000"],
    [u"河北>>邢台市>>威县", "130000000-130500000-130533000"],
    [u"河北>>邢台市>>清河县", "130000000-130500000-130534000"],
    [u"河北>>邢台市>>临西县", "130000000-130500000-130535000"],
    [u"河北>>邢台市>>南宫市", "130000000-130500000-130581000"],
    [u"河北>>邢台市>>沙河市", "130000000-130500000-130582000"],
    [u"河北>>邢台市", "130000000-130500000"],
    [u"河北>>保定市>>莲池区", "130000000-130600000-130606000"],
    [u"河北>>保定市>>新市区", "130000000-130600000-130602000"],
    [u"河北>>保定市>>北市区", "130000000-130600000-130603000"],
    [u"河北>>保定市>>南市区", "130000000-130600000-130604000"],
    [u"河北>>保定市>>白沟新城", "130000000-130600000-130605000"],
    [u"河北>>保定市>>高新区", "130000000-130600000-130611000"],
    [u"河北>>保定市>>满城县", "130000000-130600000-130621000"],
    [u"河北>>保定市>>清苑县", "130000000-130600000-130622000"],
    [u"河北>>保定市>>涞水县", "130000000-130600000-130623000"],
    [u"河北>>保定市>>阜平县", "130000000-130600000-130624000"],
    [u"河北>>保定市>>徐水县", "130000000-130600000-130625000"],
    [u"河北>>保定市>>定兴县", "130000000-130600000-130626000"],
    [u"河北>>保定市>>唐县", "130000000-130600000-130627000"],
    [u"河北>>保定市>>高阳县", "130000000-130600000-130628000"],
    [u"河北>>保定市>>容城县", "130000000-130600000-130629000"],
    [u"河北>>保定市>>涞源县", "130000000-130600000-130630000"],
    [u"河北>>保定市>>望都县", "130000000-130600000-130631000"],
    [u"河北>>保定市>>安新县", "130000000-130600000-130632000"],
    [u"河北>>保定市>>易县", "130000000-130600000-130633000"],
    [u"河北>>保定市>>曲阳县", "130000000-130600000-130634000"],
    [u"河北>>保定市>>蠡县", "130000000-130600000-130635000"],
    [u"河北>>保定市>>顺平县", "130000000-130600000-130636000"],
    [u"河北>>保定市>>博野县", "130000000-130600000-130637000"],
    [u"河北>>保定市>>雄县", "130000000-130600000-130638000"],
    [u"河北>>保定市>>涿州市", "130000000-130600000-130681000"],
    [u"河北>>保定市>>安国市", "130000000-130600000-130683000"],
    [u"河北>>保定市>>高碑店市", "130000000-130600000-130684000"],
    [u"河北>>保定市>>涿州京南经济开发区", "130000000-130600000-130699000"],
    [u"河北>>保定市", "130000000-130600000"],
    [u"河北>>定州市", "130000000-130682000"],
    [u"河北>>张家口市>>桥东区", "130000000-130700000-130702000"],
    [u"河北>>张家口市>>桥西区", "130000000-130700000-130703000"],
    [u"河北>>张家口市>>宣化区", "130000000-130700000-130705000"],
    [u"河北>>张家口市>>下花园区", "130000000-130700000-130706000"],
    [u"河北>>张家口市>>察北管理区", "130000000-130700000-130707000"],
    [u"河北>>张家口市>>塞北管理区", "130000000-130700000-130708000"],
    [u"河北>>张家口市>>开发区", "130000000-130700000-130711000"],
    [u"河北>>张家口市>>宣化县", "130000000-130700000-130721000"],
    [u"河北>>张家口市>>张北县", "130000000-130700000-130722000"],
    [u"河北>>张家口市>>康保县", "130000000-130700000-130723000"],
    [u"河北>>张家口市>>沽源县", "130000000-130700000-130724000"],
    [u"河北>>张家口市>>尚义县", "130000000-130700000-130725000"],
    [u"河北>>张家口市>>蔚县", "130000000-130700000-130726000"],
    [u"河北>>张家口市>>阳原县", "130000000-130700000-130727000"],
    [u"河北>>张家口市>>怀安县", "130000000-130700000-130728000"],
    [u"河北>>张家口市>>万全县", "130000000-130700000-130729000"],
    [u"河北>>张家口市>>怀来县", "130000000-130700000-130730000"],
    [u"河北>>张家口市>>涿鹿县", "130000000-130700000-130731000"],
    [u"河北>>张家口市>>赤城县", "130000000-130700000-130732000"],
    [u"河北>>张家口市>>崇礼县", "130000000-130700000-130733000"],
    [u"河北>>张家口市", "130000000-130700000"],
    [u"河北>>承德市>>双桥区", "130000000-130800000-130802000"],
    [u"河北>>承德市>>双滦区", "130000000-130800000-130803000"],
    [u"河北>>承德市>>营子区", "130000000-130800000-130804000"],
    [u"河北>>承德市>>开发区", "130000000-130800000-130811000"],
    [u"河北>>承德市>>承德县", "130000000-130800000-130821000"],
    [u"河北>>承德市>>兴隆县", "130000000-130800000-130822000"],
    [u"河北>>承德市>>平泉县", "130000000-130800000-130823000"],
    [u"河北>>承德市>>滦平县", "130000000-130800000-130824000"],
    [u"河北>>承德市>>隆化县", "130000000-130800000-130825000"],
    [u"河北>>承德市>>丰宁县", "130000000-130800000-130826000"],
    [u"河北>>承德市>>宽城县", "130000000-130800000-130827000"],
    [u"河北>>承德市>>围场县", "130000000-130800000-130828000"],
    [u"河北>>承德市", "130000000-130800000"],
    [u"河北>>沧州市>>新华区", "130000000-130900000-130902000"],
    [u"河北>>沧州市>>运河区", "130000000-130900000-130903000"],
    [u"河北>>沧州市>>开发区", "130000000-130900000-130911000"],
    [u"河北>>沧州市>>黄骅港开发区", "130000000-130900000-130912000"],
    [u"河北>>沧州市>>南大港管理区", "130000000-130900000-130913000"],
    [u"河北>>沧州市>>渤海新区中捷产业园区", "130000000-130900000-130914000"],
    [u"河北>>沧州市>>沧州高新技术产业开发区", "130000000-130900000-130915000"],
    [u"河北>>沧州市>>沧县", "130000000-130900000-130921000"],
    [u"河北>>沧州市>>青县", "130000000-130900000-130922000"],
    [u"河北>>沧州市>>东光县", "130000000-130900000-130923000"],
    [u"河北>>沧州市>>海兴县", "130000000-130900000-130924000"],
    [u"河北>>沧州市>>盐山县", "130000000-130900000-130925000"],
    [u"河北>>沧州市>>肃宁县", "130000000-130900000-130926000"],
    [u"河北>>沧州市>>南皮县", "130000000-130900000-130927000"],
    [u"河北>>沧州市>>吴桥县", "130000000-130900000-130928000"],
    [u"河北>>沧州市>>献县", "130000000-130900000-130929000"],
    [u"河北>>沧州市>>孟村县", "130000000-130900000-130930000"],
    [u"河北>>沧州市>>泊头市", "130000000-130900000-130981000"],
    [u"河北>>沧州市>>任丘市", "130000000-130900000-130982000"],
    [u"河北>>沧州市>>黄骅市", "130000000-130900000-130983000"],
    [u"河北>>沧州市>>河间市", "130000000-130900000-130984000"],
    [u"河北>>沧州市", "130000000-130900000"],
    [u"河北>>廊坊市>>安次区", "130000000-131000000-131002000"],
    [u"河北>>廊坊市>>广阳区", "130000000-131000000-131003000"],
    [u"河北>>廊坊市>>开发区", "130000000-131000000-131011000"],
    [u"河北>>廊坊市>>固安县", "130000000-131000000-131022000"],
    [u"河北>>廊坊市>>永清县", "130000000-131000000-131023000"],
    [u"河北>>廊坊市>>香河县", "130000000-131000000-131024000"],
    [u"河北>>廊坊市>>大城县", "130000000-131000000-131025000"],
    [u"河北>>廊坊市>>文安县", "130000000-131000000-131026000"],
    [u"河北>>廊坊市>>大厂县", "130000000-131000000-131028000"],
    [u"河北>>廊坊市>>霸州市", "130000000-131000000-131081000"],
    [u"河北>>廊坊市>>三河市", "130000000-131000000-131082000"],
    [u"河北>>廊坊市", "130000000-131000000"],
    [u"河北>>衡水市>>桃城区", "130000000-131100000-131102000"],
    [u"河北>>衡水市>>开发区", "130000000-131100000-131111000"],
    [u"河北>>衡水市>>衡水湖自然保护区", "130000000-131100000-131112000"],
    [u"河北>>衡水市>>枣强县", "130000000-131100000-131121000"],
    [u"河北>>衡水市>>武邑县", "130000000-131100000-131122000"],
    [u"河北>>衡水市>>武强县", "130000000-131100000-131123000"],
    [u"河北>>衡水市>>饶阳县", "130000000-131100000-131124000"],
    [u"河北>>衡水市>>安平县", "130000000-131100000-131125000"],
    [u"河北>>衡水市>>故城县", "130000000-131100000-131126000"],
    [u"河北>>衡水市>>景县", "130000000-131100000-131127000"],
    [u"河北>>衡水市>>阜城县", "130000000-131100000-131128000"],
    [u"河北>>衡水市>>冀州区", "130000000-131100000-131181000"],
    [u"河北>>衡水市>>深州市", "130000000-131100000-131182000"],
    [u"河北>>衡水市", "130000000-131100000"],
    [u"河北", "130000000"]
]

for reg, code in hb_region_code:
    add_start({ORIGIN_REGION: reg,
               URL: "http://www.ccgp-hebei.gov.cn/zfcg/web/getPreWinAnncList_1.html",
               ANNOUNCE_TYPE: u"预中标公告",
               PROJECT_TYPE: u"政府采购",
               METHOD: POST,
               PARAMS: {"areaCode": code, "citycode": "", "cityname": "", "prewintitle": "", "levelFlag1": ""},
               SLEEP_FOR_CONTENT: 1,
               WEBSITE: u"河北省政府采购网",
               NOTE: u"河北省政府采购网-预中标公告-政府采购"})
    add_start({ORIGIN_REGION: reg,
               URL: "http://www.ccgp-hebei.gov.cn/zfcg/web/getBidWinAnncList_1.html",
               ANNOUNCE_TYPE: u"中标公告",
               PROJECT_TYPE: u"政府采购",
               METHOD: POST,
               PARAMS: {"areaCode": code, "citycode": "", "cityname": "", "prewintitle": "", "levelFlag1": ""},
               SLEEP_FOR_CONTENT: 1,
               WEBSITE: u"河北省政府采购网",
               NOTE: u"河北省政府采购网-中标公告-政府采购"})

# 石家庄工程建设交易信息网
add_start({ORIGIN_REGION: u"河北>>石家庄",
           URL: "http://www.sjzjzsc.com/ZBGS.ASPX?pages=1",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"石家庄工程建设交易信息网",
           NOTE: u"石家庄工程建设交易信息网-中标公示-工程建设"})

# 邢台市政务服务中心
add_start({ORIGIN_REGION: u"河北>>邢台",
           URL: "http://zyjy.xtsxzfw.gov.cn:83/web/list1.aspx?columnsym=ZHONGBGG_ZFCG&Page=1&parentsym=ZHONGBGG&sort=0&title=",
           ANNOUNCE_TYPE: u"中标公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"邢台市政务服务中心",
           NOTE: u"邢台市政务服务中心-中标公告-政府采购"})
add_start({ORIGIN_REGION: u"河北>>邢台",
           URL: "http://zyjy.xtsxzfw.gov.cn:83/web/list1.aspx?columnsym=ZHONGBGG_JSGC&Page=1&parentsym=ZHONGBGG&sort=0&title=",
           ANNOUNCE_TYPE: u"中标公告",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"邢台市政务服务中心",
           NOTE: u"邢台市政务服务中心-中标公告-工程建设"})

# # TODO
# # 邢台建设信息网
# add_start({ORIGIN_REGION: u"河北>>邢台",
#            URL: "http://www.xtjsj.gov.cn/bsinfolist.asp?sortid=6&Page=1",
#            ANNOUNCE_TYPE: u"中标公示",
#            PROJECT_TYPE: u"工程建设",
#            WEBSITE: u"邢台建设信息网",
#            NOTE: u"邢台建设信息网-中标公示-工程建设"})


# 上海


# 重庆
# 重庆市政府采购网
add_start({ORIGIN_REGION: u"重庆",
           URL: "https://www.cqgp.gov.cn/gwebsite/api/v1/notices/stable?pi=1&ps=20&type=300,302,304,305",
           ANNOUNCE_TYPE: u"采购结果公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"重庆市政府采购网",
           NOTE: u"重庆市政府采购网-采购结果公告"})
# 重庆市招标投标综合网
add_start({ORIGIN_REGION: u"重庆",
           URL: "http://www.cqzb.gov.cn/class-5-45(1).aspx",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"重庆市招标投标综合网",
           NOTE: u"重庆市招标投标综合网-采购结果公告"})

# TODO 重庆各个区县公共资源交易中心
# 重庆市公共资源交易中心
add_start({ORIGIN_REGION: u"重庆",
           URL: "http://www.cqggzy.com/web/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014001003&title=&infoC=&_=1482204105579",
           ANNOUNCE_TYPE: u"中标候选人公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市公共资源交易中心",
           NOTE: u"重庆市公共资源交易中心-中标候选人公示"})
add_start({ORIGIN_REGION: u"重庆",
           URL: "http://www.cqggzy.com/web/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014001004&title=&infoC=&_=1482204105579",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市公共资源交易中心",
           NOTE: u"重庆市公共资源交易中心-中标公示"})

# 重庆綦江公共资源综合交易网
add_start({ORIGIN_REGION: u"重庆>>綦江区",
           URL: "http://www.cqqjxjy.com/LBv3/n_newslist_zz_item.aspx?ILWHBNjF4clKo8UY2fiQHA=%3d",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆綦江公共资源综合交易网",
           NOTE: u"重庆綦江公共资源综合交易网-中标公示"})
# 重庆市渝中区公共资源综合交易网
add_start({ORIGIN_REGION: u"重庆>>渝中区",
           URL: "http://www.cqyzbid.com/cqyzwz/jyxx/003001/003001004/MoreInfo.aspx?CategoryNum=003001004",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市渝中区公共资源综合交易网",
           NOTE: u"重庆市渝中区公共资源综合交易网-中标公示"})
# 重庆市大渡口区公共资源交易中心
add_start({ORIGIN_REGION: u"重庆>>大渡口区",
           URL: "http://www.ddkggzy.com/lbv3/n_newslist_zz_item.aspx?ILWHBNjF4clKo8UY2fiQHA=%3d",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市大渡口区公共资源交易中心",
           NOTE: u"重庆市大渡口区公共资源交易中心-中标公示"})
# 重庆市江北区公共资源交易中心
add_start({ORIGIN_REGION: u"重庆>>江北区",
           URL: "http://www.cqjbjyzx.gov.cn/lbWeb/n_newslist_zz_item.aspx?ILWHBNjF4clKo8UY2fiQHA==",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市江北区公共资源交易中心",
           NOTE: u"重庆市江北区公共资源交易中心-中标公示"})
# 重庆市沙坪坝区公共资源交重庆綦江公共资源综合交易网易中心
add_start({ORIGIN_REGION: u"重庆>>沙坪坝区",
           URL: "http://www.cqspbjyzx.com/LBv3/n_newslist_zz_item.aspx?ILWHBNjF4clKo8UY2fiQHA==",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市沙坪坝区公共资源交易中心",
           NOTE: u"重庆市沙坪坝区公共资源交易中心-中标公示"})
# 重庆市九龙坡区公共资源综合交易网
add_start({ORIGIN_REGION: u"重庆>>九龙坡区",
           URL: "http://www.cqjlpggzyzhjy.gov.cn/cqjl/jyxx/003001/003001002/MoreInfo.aspx?CategoryNum=003001002",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市九龙坡区公共资源综合交易网",
           NOTE: u"重庆市九龙坡区公共资源综合交易网-中标公示"})
# 重庆市南岸区公共资源交易中心
add_start({ORIGIN_REGION: u"重庆>>南岸区",
           URL: "http://www.naggzy.gov.cn/articleWeb!list.action?resourceCode=jszbgs",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市南岸区公共资源交易中心",
           NOTE: u"重庆市南岸区公共资源交易中心-中标公示"})
# 北碚区公共资源综合交易中心
add_start({ORIGIN_REGION: u"重庆>>北碚区",
           URL: "http://jyzx.beibei.gov.cn/cqbbwz/002/002001/002001004/MoreInfo.aspx?CategoryNum=002001004",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"北碚区公共资源综合交易中心",
           NOTE: u"北碚区公共资源综合交易中心-中标公示"})
# 重庆市双桥经开区公共资源交易网
add_start({ORIGIN_REGION: u"重庆>>双桥区",
           URL: "http://www.023sqjy.com/lbWeb/n_newslist_zz_item.aspx?Item=200010",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市双桥经开区公共资源交易网",
           NOTE: u"重庆市双桥经开区公共资源交易网-中标公示"})
# 重庆市渝北区公共资源招投标交易中心
add_start({ORIGIN_REGION: u"重庆>>渝北区",
           URL: "http://www.ybggb.com.cn/cqybwz/jyxx/001001/001001005/MoreInfo.aspx?CategoryNum=262661",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市渝北区公共资源招投标交易中心",
           MAX_CRAWLER_NUMBER: 1,
           NOTE: u"重庆市渝北区公共资源招投标交易中心-中标公示"})
# 重庆市巴南区行政服务和公共资源交易中心
add_start({ORIGIN_REGION: u"重庆>>巴南区",
           URL: "http://jy.bnzw.gov.cn/LBv3/n_newslist_zz.aspx?Item=100026",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市巴南区行政服务和公共资源交易中心",
           NOTE: u"重庆市重庆綦江公共资源综合交易网巴南区行政服务和公共资源交易中心-中标公示"})
# 重庆市万州区公共资源综合交易中心
add_start({ORIGIN_REGION: u"重庆>>万州区",
           URL: "http://www.wzqztb.com/wzweb/jyxx/001001/001001005/MoreInfo.aspx?CategoryNum=001001005",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市万州区公共资源综合交易中心",
           NOTE: u"重庆市万州区公共资源综合交易中心-中标公示"})
# # TODO 涪陵
# 重庆市涪陵公共资源交易信息网
add_start({ORIGIN_REGION: u"重庆>>涪陵区",
           URL: "http://www.flzbjy.com/lbWeb/n_newslist_item.aspx?Item=200010",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市涪陵公共资源交易信息网",
           NOTE: u"重庆市涪陵公共资源交易信息网-中标公示"})
# 黔江区公共资源交易中心
add_start({ORIGIN_REGION: u"重庆>>黔江区",
           URL: "http://www.qjdtc.com/LBv3/n_newslist_zz_item.aspx?Item=200010",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"黔江区公共资源交易中心",
           NOTE: u"黔江区公共资源交易中心-中标公示"})
# # TODO 长寿区
# 重庆长寿区公共资源交易网
# add_start({ORIGIN_REGION: u"重庆>>长寿区",
#            URL: "http://www.csggzyjy.com/ceinwz/WebInfo_List.aspx?newsid=5000&jsgc=00000010&zfcg=&tdjy=&cqjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=1&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=jsgc",
#            ANNOUNCE_TYPE: u"中标公示",
#            PROJECT_TYPE: u"工程建设",
#            WEBSITE: u"重庆长寿区公共资源交易网",
#            NOTE: u"重庆长寿区公共资源交易网-中标公示"})
# 江津区公共资源交易中心
add_start({ORIGIN_REGION: u"重庆>>江津区",
           URL: "http://www.jjqjyzx.com/www/site/site_index_125_0.shtml",
           ANNOUNCE_TYPE: u"评审结果公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"江津区公共资源交易中心",
           NOTE: u"江津区公共资源交易中心-评审结果公示"})
# 重庆市合川区公共资源交易中心
add_start({ORIGIN_REGION: u"重庆>>合川区",
           URL: "http://www.cqhcjy.com/lbWeb/n_newslist_zz_item.aspx?ILWHBNjF4clKo8UY2fiQHA=%3d",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市合川区公共资源交易中心",
           NOTE: u"重庆市合川区公共资源交易中心-中标公示"})
# 重庆市永川区公共资源交易中心
add_start({ORIGIN_REGION: u"重庆>>永川区",
           URL: "http://www.yczyjy.cn/WebSite/ProDeal/List.aspx?cid=003001004&fid=003",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市永川区公共资源交易中心",
           NOTE: u"重庆市永川区公共资源交易中心-中标公示"})
# # 重庆市南川区公共资源综合交易中心
add_start({ORIGIN_REGION: u"重庆>>南川区",
           URL: "http://www.ncggjy.com/lbWeb/n_newslist_zz_item.aspx?Item=200010",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市南川区公共资源综合交易中心",
           NOTE: u"重庆市南川区公共资源综合交易中心-中标公示"})
# 重庆市潼南公共资源交易中心所有
add_start({ORIGIN_REGION: u"重庆>>潼南县",
           URL: "http://www.cqtnjy.com/lbv3/n_newslist_zz_item.aspx?Item=200010",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市潼南公共资源交易中心所有",
           NOTE: u"重庆市潼南公共资源交易中心所有-中标公示"})
# 重庆市铜梁区公共资源综合交易中心
add_start({ORIGIN_REGION: u"重庆>>铜梁区",
           URL: "http://www.tljyzx.com/lbv3/n_newslist_zz_item.aspx?Item=200010",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市铜梁区公共资源综合交易中心",
           NOTE: u"重庆市铜梁区公共资源综合交易中心-中标公示"})
# 重庆市大足区公共资源综合交易服务中心
add_start({ORIGIN_REGION: u"重庆>>大足区",
           URL: "http://www.cqdzjyzx.com/lbWeb/n_newslist_zz_item.aspx?Item=200010",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市大足区公共资源综合交易服务中心",
           NOTE: u"重庆市大足区公共资源综合交易服务中心-中标公示"})
# 重庆市荣昌区公共资源交易中心
add_start({ORIGIN_REGION: u"重庆>>荣昌区",
           URL: "http://zyjy.rongchang.gov.cn/WEB/PageTradingCenter/index_list.jsp?pageId=360403",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市荣昌区公共资源交易中心",
           NOTE: u"重庆市荣昌区公共资源交易中心-中标公示"})
# 重庆市璧山区公共资源交易中心
add_start({ORIGIN_REGION: u"重庆>>璧山区",
           URL: "http://www.bsggjy.com/n_newslist_zz_item.aspx?Item=200010",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市璧山区公共资源交易中心",
           NOTE: u"重庆市璧山区公共资源交易中心-中标公示"})
# 重庆市梁平县公共资源交易中心
add_start({ORIGIN_REGION: u"重庆>>梁平县",
           URL: "http://www.cqlpjyzx.com/ceinwz/webInfo_List.aspx?jsgc=0000010&newsid=10005&FromUrl=jsgc",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市梁平县公共资源交易中心",
           NOTE: u"重庆市梁平县公共资源交易中心-中标公示"})
# 城口县公共资源交易中心
add_start({ORIGIN_REGION: u"重庆>>城口县",
           URL: "http://www.ckjyzx.cn/LBv3/n_newslist_zz_item.aspx?Item=200010",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"城口县公共资源交易中心",
           NOTE: u"城口县公共资源交易中心-中标公示"})
# 重庆市丰都县公共资源交易中心
add_start({ORIGIN_REGION: u"重庆>>丰都县",
           URL: "http://www.fdggzy.cn/lbWeb/n_newslist_zz_item.aspx?ILWHBNjF4clKo8UY2fiQHA=%3d",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市丰都县公共资源交易中心",
           NOTE: u"重庆市丰都县公共资源交易中心-中标公示"})
# 重庆市垫江县公共资源交易中心
add_start({ORIGIN_REGION: u"重庆>>垫江县",
           URL: "http://www.djjyzx.gov.cn/lbweb/n_newslist_zz_item.aspx?Item=200010",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市垫江县公共资源交易中心",
           NOTE: u"重庆市垫江县公共资源交易中心-中标公示"})
# 重庆市武隆县公共资源综合交易中心
add_start({ORIGIN_REGION: u"重庆>>武隆县",
           URL: "http://www.wlzyzx.cn/ceinwz/msjyjggs.aspx?xmlx=10&FromUrl=msjyjggs.htm&zbdl=1",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市武隆县公共资源综合交易中心",
           NOTE: u"重庆市武隆县公共资源综合交易中心-中标公示"})
# 重庆市忠县公共资源综合交易中心
add_start({ORIGIN_REGION: u"重庆>>忠县",
           URL: "http://www.zxggzy.cn/lbWeb/n_newslist_zz_item.aspx?Item=200010",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市忠县公共资源综合交易中心",
           NOTE: u"重庆市忠县公共资源综合交易中心-中标公示"})
# 重庆市开州区公共资源交易网
add_start({ORIGIN_REGION: u"重庆>>开州区",
           URL: "http://www.cqkxjyzx.com/ceinwz/msjyjggs.aspx?xmlx=10&FromUrl=msjyjggs.htm&zbdl=1&newsid=0",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市开州区公共资源交易网",
           NOTE: u"重庆市开州区公共资源交易网-中标公示"})
# 云阳县公共资源交易服务中心
add_start({ORIGIN_REGION: u"重庆>>云阳县",
           URL: "http://www.yyggzyjy.com/Frame/BulletinList.aspx?BusinessType=2&InfoType=2",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"云阳县公共资源交易服务中心",
           NOTE: u"云阳县公共资源交易服务中心-中标公示"})
# 重庆市奉节县公共资源综合交易中心
add_start({ORIGIN_REGION: u"重庆>>奉节县",
           URL: "http://www.fjjyzx.net/lbWeb/n_newslist_zz_item.aspx?Item=200010",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市奉节县公共资源综合交易中心",
           NOTE: u"重庆市奉节县公共资源综合交易中心-中标公示"})
# 重庆巫山公共资源交易中心
add_start({ORIGIN_REGION: u"重庆>>巫山县",
           URL: "http://www.wsggzyjy.com/lbWeb/n_newslist_zz_item.aspx?ILWHBNjF4clKo8UY2fiQHA=%3d",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆巫山公共资源交易中心",
           NOTE: u"重庆巫山公共资源交易中心-中标公示"})
# 重庆巫溪县公共资源综合交易中心
add_start({ORIGIN_REGION: u"重庆>>巫溪县",
           URL: "http://www.wuxifz.com/articleWeb!list.action?resourceCode=jszbgs",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆巫溪县公共资源综合交易中心 ",
           NOTE: u"重庆巫溪县公共资源综合交易中心 -中标公示"})
# 重庆市石柱土家族自治县公共资源交易中心
add_start({ORIGIN_REGION: u"重庆>>石柱土家族自治县",
           URL: "http://www.cqszggzyjy.com/lbv3/n_newslist_zz_item.aspx?+CrZgb12k3hKo8UY2fiQHA==",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"重庆市石柱土家族自治县公共资源交易中心",
           NOTE: u"重庆市石柱土家族自治县公共资源交易中心-中标公示"})
# 秀山土家族苗族自治县公共资源综合交易中心
add_start({ORIGIN_REGION: u"重庆>>秀山土家族苗族自治县",
           URL: "http://www.xsggzy.com/lbWeb/n_newslist_zz_item.aspx?Item=200010",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"秀山土家族苗族自治县公共资源综合交易中心",
           NOTE: u"秀山土家族苗族自治县公共资源综合交易中心-中标公示"})
# 酉阳公共资源交易网
add_start({ORIGIN_REGION: u"重庆>>酉阳土家族苗族自治县",
           URL: "http://www.yyggzy.com/lbWeb/n_newslist_zz_item.aspx?Item=200010",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"酉阳公共资源交易网",
           NOTE: u"酉阳公共资源交易网-中标公示"})
# 彭水县公共资源交易网
add_start({ORIGIN_REGION: u"重庆>>彭水县",
           URL: "http://www.psggzy.com/main/jyjggg/gcjyjjgg/index.shtml",
           ANNOUNCE_TYPE: u"中标公示",
           PROJECT_TYPE: u"工程建设",
           WEBSITE: u"彭水县公共资源交易网",
           NOTE: u"彭水县公共资源交易网-中标公示"})

# 天津
# 天津市政府采购网
add_start({ORIGIN_REGION: u"天津",
           URL: "http://www.tjgp.gov.cn/portal/topicView.do",
           METHOD: POST,
           PARAMS: {"method": "view",
                    "page": 1,
                    "id": 2014,
                    "step": 1,
                    "view": "Infor",
                    "st": 1},
           ANNOUNCE_TYPE: u"采购结果公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"天津市政府采购网",
           NOTE: u"天津市政府采购网-采购结果公告"})

# 北京
# 北京市招投标公共服务平台
add_start({ORIGIN_REGION: u"北京",
           URL: "http://www.bjztb.gov.cn/zbjg_2015/index.htm",
           ANNOUNCE_TYPE: u"中标结果",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"北京市招投标公共服务平台",
           NOTE: u"北京市招投标公共服务平台-中标结果-2015-9-14后数据"})

# 全国

# 中国国际招标网
zoneCodes = ["11*", "12*", "13*", "14*", "15*",
             "21*", "22*", "23*",
             "31*", "32*", "33*", "34*", "35*", "36*", "37*",
             "41*", "42*", "43*",
             "50*", "51*", "52*", "53*", "54*",
             "61*", "62*", "63*", "64*", "65*"]
for zoneCode in zoneCodes:
    add_start({ORIGIN_REGION: u"全国",
               URL: "http://www.chinabidding.com/search/proj.htm",
               ANNOUNCE_TYPE: u"中标结果公告",
               METHOD: POST,
               PARAMS: {"infoClassCodes": "0108", "poClass": "BidResult", "currentPage": "1",
                        "zoneCode": zoneCode},
               WEBSITE: u"中国国际招标网",
               SLEEP_SECOND: 3,
               NOTE: u"中国国际招标网-中标结果公告"})

# TODO
# 中国政府采购招标网
add_start({ORIGIN_REGION: u"全国",
           URL: "http://www.chinabidding.org.cn/LuceneSearch.aspx?kwd=&filter=b3-0-0-keyword-360",
           ANNOUNCE_TYPE: u"中标公告",
           METHOD: POST,
           PARAMS: {"AspNetPager": "1"},
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"中国政府采购招标网",
           NOTE: u"中国政府采购招标网-中标公告"})

# 中国电子招标信息网
add_start({ORIGIN_REGION: u"全国",
           URL: "http://www.zbs365.com/zhongbiao/type-p1.html",
           ANNOUNCE_TYPE: u"中标公告",
           WEBSITE: u"中国电子招标信息网",
           NOTE: u"中国电子招标信息网-中标公告"})

# 中国政府采购网
add_start({ORIGIN_REGION: u"全国",
           URL: "http://www.ccgp.gov.cn/cggg/zygg/zbgg/index.htm",
           ANNOUNCE_TYPE: u"中标公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"中国政府采购网",
           NOTE: u"中国政府采购网-中央标讯-中标公告"})
add_start({ORIGIN_REGION: u"全国",
           URL: "http://www.ccgp.gov.cn/cggg/zygg/cjgg/index.htm",
           ANNOUNCE_TYPE: u"成交公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"中国政府采购网",
           NOTE: u"中国政府采购网-中央标讯-成交公告"})
add_start({ORIGIN_REGION: u"全国",
           URL: "http://www.ccgp.gov.cn/cggg/dfgg/zbgg/index.htm",
           ANNOUNCE_TYPE: u"中标公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"中国政府采购网",
           NOTE: u"中国政府采购网-地方标讯告-中标公告"})
add_start({ORIGIN_REGION: u"全国",
           URL: "http://www.ccgp.gov.cn/cggg/dfgg/cjgg/index.htm",
           ANNOUNCE_TYPE: u"成交公告",
           PROJECT_TYPE: u"政府采购",
           WEBSITE: u"中国政府采购网",
           NOTE: u"中国政府采购网-地方标讯-成交公告"})

# 中国政府采购网-搜索结果
add_start({ORIGIN_REGION: u"全国",
           URL: "http://search.ccgp.gov.cn/bxsearch",
           ANNOUNCE_TYPE: u"中标公告",
           PROJECT_TYPE: u"政府采购",
           SLEEP_SECOND: 5,
           WEBSITE: u"中国政府采购网",
           NOTE: u"中国政府采购网-中央标讯-中标公告"})


print json.dumps(start_urls,indent=2,ensure_ascii=False)