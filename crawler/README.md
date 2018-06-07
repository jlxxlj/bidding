# 招投标爬虫

> 从全国各个地区招投标公示网站爬取招投标结果公告


## 项目目录内容

```
./
├── TMP_WORK/  临时任务，不经常使用
├── config/  配置
├── db/  数据库接口
├── parser_helper/  公告页面解析的辅助方法
├── test/  测试
├── cathe_manage.py  管理url缓存的脚本
├── content_saver.py  保存爬取的原始公告
├── crawler_monitor.py  [未使用]
├── crawler.py  爬虫
├── crawler_runner.py  启动爬虫方法
├── deploy.py  部署脚本
├── page_parser.py  具体公告页面解析方法
├── page_start.py  所有招投标公告源
├── policy.py  爬虫启动策略
├── queue.py  进程内消息queue
├── README.md
├── requirements.txt
├── start_crawler.py  爬虫启动脚本，可以设置启动参数
├── task.py  [未使用]
├── test.py  [未使用]
├── url_pool.py  管理爬虫爬过的url地址
└── util.py  自定义工具包
```


## 爬虫启动

* [启动脚本](/crawler/start_crawler.py)

* 参数

```
Usage:
	python start_crawler.py [options]

Options:
	--policy=<policy_file>     	policy file
	--policy_type=<policy_type>	policy type
                                    	# 爬虫启动策略
                                    	# 0. 启动一个Queue负责所有的消息
                                    	# 1. 每个省启动一个Queue负责每个省的所有消息
                                    	# 2. 每个网站启动一个Queue负责每个网站的所有消息
                                    	# 3. 每个源启动一个Queue负责每个源的所有消息

	--crawler_type=<type>      	crawler type(1:全量爬取, 2:定时爬取), default is 1
	--crawler_number=<number>  	set the thread number of crawler, default is 3
	--filter_region=<region>   	set the origin region to crawl
	--filter_url=<url>         	set the url to crawl
	--apply_time_interval      	set crawler will check the announce publish time
	--time_st=<start_time>     	set time interval's start, default is 30 days before
	--time_ed=<end_time>       	set time interval's end
	-h, --help                 	show script usage

```

* 爬虫运行流程
    1. start_crawler.py  根据参数确定的爬取的源，爬取方式，爬虫线程个数去启动爬虫
    2. crawler_runner.py  根据设置的参数启动爬虫线程
    3. crawler.py  执行公告爬取任务

## 公告爬取
* 爬取过程
    从对应的queue里面取出一条消息，获取对应页面，将获取的页面源码html交给对应page_paser方法去解析，解析后会返回
    还需要爬取的页面地址（一般是公告下一页）以及解析好了的公告详细内容，将还需要爬取的消息推送到对应queue里，将解析好的结果
    保存。
