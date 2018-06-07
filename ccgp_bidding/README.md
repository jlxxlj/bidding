# 招投标项目说明

标签（空格分隔）： 未分类

---

## 数据源：

网站名：中国政府采购网(http://www.ccgp.gov.cn/)

爬取URL：http://search.ccgp.gov.cn/dataB.jsp?searchtype=1&page_index=1&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=11&dbselect=bidx&kw=&start_time=2016%3A09%3A04&end_time=2016%3A09%3A07&timeType=1&displayZone=&zoneId=&pppStatus=&agentName=

公告样例URL：http://www.ccgp.gov.cn/cggg/zygg/zbgg/201609/t20160907_7286790.htm

## 爬取方式

全量爬取 + 定时增量爬取(每天晚上12点)

## 数据量

2001-01-01～2016-09-06 中国政府采购网上共有2,000,000左右条（中标公告 + 成交公告）数据

## 解析率

1.29中标公司 / 1条公告

## 公告解析结果字段：
```

{
    "purchaser":"青龙满族自治县军队离退休干部休养所",                               # 招标人
    "purchase_agent":"秦皇岛国民工程咨询有限公司",                                  # 招标代理人
    "purchase_category":"工程/其他建筑工程",                                        # 招标项目品目
    "title":"青龙满族自治县军队离退休干部休养所装修工程成交公告",                   # 公告标题
    "url":"http://www.ccgp.gov.cn/cggg/dfgg/cjgg/201602/t20160205_6519820.htm",     # 公告地址
    "region":"河北",                                                                # 所属行政区域
    "published_ts":"2016-02-05 08:41:05",                                           # 公告时间
    "announced_ts":"2016-01-25 00:00:00",                                           # 本项目招标公告日期
    "winning_ts":"2016-02-04 00:00:00",                                             # 成交日期
    "announce_type":"成交公告",                                                     # 公告类型
    "amount":46.315312,                                                             # 总成交金额
    "unit":"万元",                                                                  # 总成交金额单位
    "currency":"人民币",                                                            # 总成交金额币种
    "analysis_result":{                                                             # 招投标文档解析结果
        "bid_result":[                                                              # 中标单位及金额结果
            {"winning_company":"秦皇岛顺安建筑工程有限公司",                        # 中标单位名称
            "winning_amount":463153.12,                                             # 中标金额
            "unit":,"元",                                                           # 中标金额单位
            "currency":"人民币"                                                     # 中标金额币种
            }
        ],
        "bid_time":"2016-02-04 00:00:00"                                            # 解析出的中标日期
        }
    }

```

## 数据覆盖率
```

{
    "purchaser":"",#招标人                         #总条数 33544    #覆盖率 100%
    "purchase_agent":"",#招标代理人                  #总条数 33544    #覆盖率 100%
    "purchase_category":"",#招标项目品目              #总条数 33544    #覆盖率 100%
    "title":"",#公告标题                             #总条数 33544    #覆盖率 100%
    "url":"",#公告地址                              #总条数 33544    #覆盖率 100%
    "region":"",#所属行政区域                        #总条数 33544    #覆盖率 100%
    "published_ts":"",#公告时间                       #总条数 33544    #覆盖率 100%
    "announced_ts":"",#本项目招标公告日期            #总条数 33544    #覆盖率 45%
    "winning_ts":"",#成交日期                        #总条数 33544    #覆盖率 100%
    "announce_type":"",#公告类型                    #总条数 33544    #覆盖率 100%
    "amount":,#总成交金额                            #总条数 33544    #覆盖率 26%
    "unit":"",#总成交金额单位                         #总条数 33544    #覆盖率 26%
    "currency":"",#总成交金额币种                     #总条数 33544    #覆盖率 26%
    "analysis_result":{
        "bid_result":[
            {"winning_company":"",#中标单位名称       #总条数 43075    #覆盖率 100%
            "winning_amount":,#中标金额             #总条数 43075    #覆盖率 86%
            "unit":"",#中标金额单位                   #总条数 43075    #覆盖率 83%
            "currency":"",#中标金额币种               #总条数 43075    #覆盖率 44%
            }
        ]
        }
    }

```
