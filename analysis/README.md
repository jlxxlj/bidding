# 招投标原始数据解析

> 将网上爬取招投标原始数据进行解析，抽取中标信息

## 项目目录内容

```
./
├── TMP_WORK/  临时任务
├── config/  配置
├── db/  数据库
├── scu_ner/  实体识别
├── services/  服务
├── test/  测试
├── toolkit/  工具包（地址补全）
├── announce_analysis.py  招投标公告监控的解析主方法
├── announce_analysis_result_key_map.py  解析结果到数据库表的映射
├── announce_analysis_result_save.py  将解析的招投标结果保存到数据库
├── announce_attributes.py  定义招投标公告属性
├── deploy.py  部署脚本
├── html_convert_to_dict.py  将html按文档内容进行分段、转换成层级表示
├── html_dict_analysis.py  从转换后的文档中抽取关键信息，并进行组合
├── html_purify.py  将爬取的原始数据html进行精简
├── obtain_element_info.py  从文本中抽取元信息
├── README.md
├── regulations.py  设置招投标信息抽取规则
├── requirments.txt
├── result_template.py  解析结果模板
├── test_anaylysis.py  测试解析方法
└── util.py  自定义工具变量及函数
```

## 解析流程
1. 从AWS-SQS中取最新爬取的公告消息，按消息中的object key 读取爬取的原始公告数据； [详细](/analysis/announce_analysis.py)
2. 将爬取的原始数据html进行精简； [详细](/analysis/html_purify.py)
3. 将html按文档内容进行分段、转换成层级表示； [详细](/analysis/html_convert_to_dict.py)
4. 从转换后的文档中抽取关键信息，并进行组合； [详细](/analysis/html_dict_analysis.py)
5. 将结果保存到 阿里云的postgreSQL。 [详细](/analysis/announce_analysis_result_save.py)

## 服务
1. [实体识别服务](/analysis/services/ner_service.py)
2. [结果保存到阿里云的postgreSQL的服务](/analysis/services/announce_analysis_result_save_service.py)

## 工具
* **地址补全：** 根据输入的地址，将地址的省、市、县各级全称等进行补全

