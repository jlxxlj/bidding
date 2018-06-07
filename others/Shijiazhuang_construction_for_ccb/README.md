# 招投标--重庆建设银行任务

> 为重庆建设银行推送最新的重庆地区工程建设招投标的中标结果

## 项目目录内容

```
-- data/ 已经推送了的公告数据
-- config.py 任务配置
-- daily_word.py 推送脚本
-- deploy.py 部署脚本
```

## 部署

* [部署脚本](others/Chongqing_construction_for_ccb/deploy.py)

* 部署方式

> 本地部署：主机 192.168.31.114

> crontab 每天早上9点启动脚本推送

## 推送方式

> 从招投标结果表 bidding_announce、bidding_result 中查出最近30天重庆地区所有工程建设相关的中标信息，
将这些中标信息与已经推送了的公告（存在本地sqlite：./data/announce.db），对还没有推送过的公告补全中标公司联系方式，
最后推送到指定邮箱。
