#  -*- coding:utf-8 -*-

import re

INDEX_SEPARATOR = [u"、", u".", u"）", u")"]  # 编号后面的分割符号
KEY_VALUE_SEPARATOR = [u":", u"：", u";", u"；"]
CN_PUNCTUATION = u"·×—‘’“”…、。《》『』【】!（），：；？"
EN_PUNCTUATION = u"!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
BLANK = " \t\n"

CN_SIMPLE_NUMBER = u"零一二三四五六七八九十百千万亿"

CN_COMPLEX_NUMBER = u"零壹贰叁肆伍陆柒捌玖拾佰仟万亿"

DICT_CN_SIMPLE_NUMBER = {u"零": 0, u"一": 1, u"二": 2, u"三": 3, u"四": 4, u"五": 5, u"六": 6, u"七": 7,
                         u"八": 8, u"九": 9, u"十": 10, u"百": 100, u"千": 1e3, u"万": 1e4, u"亿": 1e8}

DICT_CN_COMPLEX_NUMBER = {u"零": 0, u"壹": 1, u"贰": 2, u"叁": 3, u"肆": 4, u"伍": 5, u"陆": 6, u"柒": 7,
                          u"捌": 8, u"玖": 9, u"拾": 1e1, u"佰": 1e2, u"仟": 1e3, u"万": 1e4, u"亿": 1e8}

DICT_NUMBER = {u"0": 0, u"1": 1, u"2": 2, u"3": 3, u"4": 4, u"5": 5, u"6": 6, u"7": 7, u"8": 8, u"9": 9}  # 阿拉伯数字编号

# 定义关键词进行表格处理
BID_COMPANY_PATTERN = u"(?:中标|成交|投标)(?:候选|)(?:单位|供应商|供货商|商|人)"
BID_MONEY_PATTERN = u"(?:中标|成交|投标|竞标|)(?:单位|供应商|供货商|商|人|)(?:总|单|)(?:金额|报价|价格|价)"

KEYWORDS = [u'项目名', u'项目名称', u'项目编号', u'项目联系人', u'采购项目', u'项目联系电话', u'项目经理', u'项目负责人',

            u'联系方式', u'小组成员', u'时间', u"日期", u'地点', u'地址', u'编号', u'公告媒体', u'评标小组组长',

            u'采购人', u'招标人', u'采购单位', u'采购代理', u'采购方式', u'采购编号', u'采购单位', u'采购内容', u'采购结果',
            u'采购预算', u'采购金额', u'采购数量', u'采购机构', u'采购计划',

            u'评标小组成员名单', u'代理机构', u'中标信息', u'评标委员会成员名单', u'规格型号', u'数量', u'单价', u'服务要求', u'联系人', u'联系电话', u'评审情况',
            u'发布媒介', u'招标文件售价', u'招标文件获取方式', u'预算控制价', u'评标委员', u'招标范围', u'专家名单', u'质保期', u'大写',
            u'成交价', u'谈判文件', u'工期', u'供货商信息', u'中标（成交）信息:', u'具体情况如下', u'名称', u'成交结果', u'安全员', u'公示媒介', u'质疑和投诉',
            u'投诉受理部门', u'投诉受理电话', u'结构类型及规模', u'招标代理机构', u'招标类别', u'招标方式', u'序号', u'总报价', u'排序', u'中标产品型号', u'包号',
            u'商品', u'品牌', u'型号', u'预算价', u'备注', u'单位', u'供应商', u'单价', u'报价', u'中标候选人', u'总价', u'质量', u'金额', u'市场价格',
            u'得分', u'排名', u'合同包', u'中标候选人', u'工商注册号', u'组织机构代码', u'中标结果', u'入围单位', u'名次', u'中标公示信息', u'', u'', u'', u'']


def type_of_text(text):
    # 有三种类型：1.关键字 2.值 3.键值一起
    text = re.sub(" ", "", text)
    text = re.sub("\(.*\)|（.*）", "", text)
    text = text.strip().strip(":").strip(u"：")
    if re.search(u"[:：]+", text) is not None:
        return "kv"
    # 关键字最大长度不超过20
    if len(text) > 30:
        return "v"
    # 是一个句子而不是一个短语
    if re.search(u"[，；。！？,;!?]+", text) is not None:
        return "v"
    # # 不能有有数字和字母
    if re.search(u"[0-9a-zA-Z壹贰叁肆伍陆柒捌玖拾佰]+", text) is not None:
        return "v"
    if re.search(BID_COMPANY_PATTERN, text) is not None:
        return "k"
    if re.search(BID_MONEY_PATTERN, text) is not None:
        return "k"
    for kw in KEYWORDS:
        if kw is u"":
            continue
        if kw in text:
            return "k"
    return "v"


def split_text(partern, text):
    # 按partern给出的正则表达式对text进行分割, 去是掉空白的结果
    items = re.split(partern, text)
    items = [x.strip() for x in items if len(x.strip()) > 0]
    return items


def convert_cn_number(cn_number):
    """
    将大写的金额数字转换成float型，不做格式检查
    :param cn_number:
    :return:
    """
    tmp = []
    dict_cn_number = {u"角": 1e-1, u"分": 1e-2}
    dict_cn_number.update(DICT_CN_SIMPLE_NUMBER)
    dict_cn_number.update(DICT_CN_COMPLEX_NUMBER)
    for number in cn_number:
        if number in dict_cn_number:
            v = dict_cn_number.get(number)
            if v >= 1e1 and len(tmp) == 0:  # 金额是"拾、佰..."开头的情况
                tmp.append([v, v])
            elif v >= 1e1:  # 金额单位
                t = 0
                i = 0
                for i in range(len(tmp) - 1, -1, -1):
                    if v > tmp[i][0]:
                        t += tmp[i][1]
                    else:
                        i += 1
                        break
                tmp = tmp[:i]
                tmp.append([v, t * v])
            elif 1e-1 >= v > 0:
                tmp[-1][0] = v
                tmp[-1][1] *= v
            else:
                tmp.append([1, v])  # 默认单位为1
    result = sum([x[1] for x in tmp])
    return result


# 公司后缀情况
# 公司
SUFFIX_GONGSHI = []
# 厂
SUFFIX_CHANG = [u"修理", u"修配", u"仪器", u"家具", u"设备", u"维修", u"服装", u"机械", u"印刷", u"器械", u"制造", u"头盔", u"保养", u"加工",
                u"装总", u"器总", u"装备", u"材总", u"器材", u"制品", u"港船", u"修造", u"改装", u"刷三", u"牌照", u"械总", u"电器", u"软垫",
                u"用品", u"合肥", u"药总", u"药品", u"造船", u"汽车", u"衣总", u"阳灶", u"件柜", u"标本", u"门总", u"化工", u"品六", u"备总",
                u"灯具", u"汽修", u"来水", u"水泥", u"工艺", u"艺品", u"制帽", u"光缆", u"被服", u"车辆", u"装具", u"瓶车", u"客车", u"水泵",
                u"开关", u"制衣", u"福利", u"电缆", u"农药", u"电梯", u"材料", u"彩印", u"舱总", u"证照", u"璃钢", u"锅炉", u"制药", u"服二",
                u"造总", u"二工", u"电料", u"标牌", u"徽章", u"教具", u"家俱", u"塑料", u"容器", u"面砖", u"仪表", u"装车", u"岗石", u"火器",
                u"船二", u"轮车", u"实验", u"动门", u"织品", u"大米", u"压器", u"洁具", u"岗岩", u"金属", u"机床", u"印钞", u"五金", u"工具",
                u"锚链", u"综合", u"水表", u"木器", u"绳网", u"蔽室", u"线电", u"字牌", u"绳业", u"制修", u"玩具", u"成套", u"辰工", u"录纸",
                u"门窗", u"电炉", u"彩砖", u"司船", u"乳胶", u"预制", u"帘门", u"农机", u"石材", u"港机", u"柜分", u"马船", u"模型", u"电杆",
                u"关二", u"环保", u"物肥", u"闸门", u"试剂", u"丝印", u"装潢", u"家私", u"达船", u"所药", u"泥新", u"棉织", u"制件", u"汽保",
                u"程船", u"灯饰", u"风机", u"机电", u"燃具", u"器具", u"钢具", u"选矿", u"教仪", u"铸造", u"油箱", u"械工", u"木材", u"路灯",
                u"辅机", u"修一", u"美术", u"构件", u"电四", u"混肥", u"陶瓷", u"附件", u"棉胎", u"电瓷", u"化肥", u"酸泵", u"钢板", u"饲料",
                u"蝶阀", u"公司", u"照明", u"衡器", u"椅业", u"山水", u"装配", u"具分", u"机总", u"炮总", u"铸机", u"线漆", u"服饰", u"洗煤",
                u"管桩", u"建材", u"沙发", u"冲压", u"杀虫", u"电总", u"科技", u"雕塑", u"关砖", u"电子", u"市船", u"手套", u"泥制", u"织造",
                u"山茶", u"型煤", u"关船", u"轻纺", u"量器", u"兴米", u"雕刻", u"生瓷", u"温管", u"亭船", u"化布", u"轮椅", u"电柱", u"校具",
                u"园艺", u"煤炉", u"沙船", u"片石", u"机车", u"属工", u"五工", u"行车", u"四砖", u"理石", u"盗门", u"防车", u"用具", u"七工",
                u"养殖", u"被装", u"利米", u"面粉", u"布总", u"时装", u"关柜", u"薄膜", u"动房", u"皮带", u"大修", u"县水", u"钢船", u"线杆",
                u"铁柜", u"排灌", u"虫剂", u"地砖", u"京分", u"电材", u"被单", u"厨具", u"铁塔", u"却器", u"合金", u"笼具", u"焦化", u"阀门",
                u"黑板", u"湾砖", u"翻新", u"石料", u"装饰", u"冷冻", u"制口", u"七一", u"配件", u"防护", u"应用", u"电线", u"力米", u"道砖",
                u"模具", u"网套", u"石雕", u"品一", u"设施", u"灌机", u"涂料", u"兽药", u"利鞋", u"六二", u"配套", u"礼品", u"制片", u"四工",
                u"滴管", u"配一", u"食品", u"具总", u"煤球", u"茗茶", u"管件", u"衬衫", u"维护", u"包装", u"气片", u"缆总", u"新船", u"装璜",
                u"兴煤", u"表总", u"校服", u"电表", u"大棚", u"试验", u"制服", u"坊分", u"燥机", u"棉被", u"平台", u"邮票", u"座椅", u"麻石",
                u"机肥", u"剧装", u"偿器", u"虹灯", u"械二"]
# 院
SUFFIX_YUAN = [u"医", u"学", u"分", u"总", u"病", u"研究", u"设计", u"勘察", u"保健", u"测绘", u"博物", u"调查", u"规划", u"勘查", u"勘测",
               u"工程", u"绘总", u"监测", u"究生", u"技术", u"疗养", u"地图", u"影剧", u"京剧", u"机械", u"开发", u"舞剧", u"考试", u"建研", u"防治",
               u"卫生", u"电影", u"遥感", u"地调", u"雕塑", u"星剧", u"检测", u"家大"]
# 所
SUFFIX_SUO = [u"分", u"研究", u"事务", u"检验", u"管理", u"监理", u"休养", u"管教", u"设计", u"招待", u"研三", u"监督", u"印刷", u"科研", u"车管",
              u"调查", u"防治", u"测绘", u"制作", u"力学", u"电子", u"修理", u"能源", u"营业", u"理化", u"研制", u"编码", u"十三", u"十九", u"检修",
              u"监测", u"苗圃", u"水泥", u"研发", u"林科", u"十二"]
# 部
SUFFIX_BU = [u"经营", u"经销", u"服务", u"批发", u"经理", u"宣传", u"门市", u"事业", u"组织", u"家电", u"销售", u"科研", u"修理", u"安装", u"制作",
             u"装饰", u"俱乐", u"工程", u"维修", u"器械", u"购销", u"零批", u"工作", u"批零", u"汽配", u"指挥", u"电脑", u"营业", u"直销", u"器材",
             u"营销", u"设计", u"发展", u"印刷", u"后勤", u"发行", u"广告", u"加工", u"策划", u"特销", u"装璜", u"开发", u"贸易", u"装潢", u"汽修",
             u"材料", u"打印", u"工贸", u"产业", u"印务", u"石刻", u"装备", u"制衣", u"培训", u"草业", u"项目", u"配件", u"京分", u"电器", u"配送",
             u"门窗", u"制冷", u"通讯", u"科技", u"商贸"]
# 处
SUFFIX_CHU = [u"工程", u"管理", u"经销", u"安装", u"代表", u"服务", u"供销", u"购销", u"经营", u"供应", u"稽征", u"办事", u"配件", u"监理", u"器械",
              u"销售", u"直销", u"公证", u"施工", u"接待", u"建设", u"筹建", u"园艺", u"园林", u"城管", u"调查"]
# 局
SUFFIX_JU = [u"备分", u"公安", u"管理", u"税务", u"邮政", u"统计", u"体育", u"档案", u"保护", u"发行", u"水文", u"工程", u"开发", u"邮电", u"地震",
             u"勘测", u"资源", u"干部", u"改革", u"地质", u"测绘", u"产权", u"稽征", u"旅游", u"服务", u"勘查", u"渔业", u"保密", u"教育", u"检疫",
             u"林业"]
# 厅
SUFFIX_TING = [u"公安", u"农业", u"司法", u"办公", u"林业", u"合作", u"保障", u"建设", u"产业", u"财政", u"审计", u"交通", u"资源", u"卫生", u"技术",
               u"安全", u"文化", u"教育", u"水利", u"家具", u"事务"]
# 中心
SUFFIX_ZHONGXIN = [u"服务", u"销售", u"培训", u"技术", u"信息", u"维修", u"发展", u"开发", u"管理", u"监测", u"科技", u"检测",
                   u"仪器", u"研究", u"事务", u"汇展", u"设备", u"控制", u"商务", u"种植", u"投标", u"监理", u"教育", u"印刷", u"营销", u"奶牛",
                   u"通信", u"繁育", u"贸易", u"发射", u"商贸", u"交流", u"科贸", u"经营", u"招标", u"网络", u"鉴定", u"印务", u"制作", u"咨询",
                   u"设计", u"工程", u"测试", u"养护", u"苗木", u"绿化", u"美容", u"批发", u"收看", u"美食", u"供应", u"购销", u"配送", u"电脑",
                   u"发行", u"园艺", u"计算", u"气候", u"研制", u"教考", u"安装", u"研发", u"物资", u"血液", u"家居", u"防治", u"推广", u"遥感",
                   u"处理", u"旅游", u"评估", u"出版", u"电子", u"会议", u"博览", u"文印", u"评审", u"指导", u"假肢", u"测评", u"训练", u"配件",
                   u"培育", u"精液", u"测绘", u"评价", u"警报", u"收押", u"租赁", u"制版", u"软件", u"传播", u"修理", u"洗涤", u"评测", u"器材",
                   u"装备", u"输出", u"调查", u"预报", u"建材", u"整理", u"环保", u"经销", u"国际", u"批销", u"调训", u"经贸", u"保养", u"购物",
                   u"图片", u"图书", u"认证", u"加工", u"电料", u"百货", u"动化", u"监管", u"制衣", u"直销", u"乐器", u"家具", u"配镜", u"客运",
                   u"实验", u"援助", u"美居", u"监察", u"资料", u"护卫", u"传媒", u"接待", u"音响", u"辐射", u"登记", u"华茂", u"保证", u"处置",
                   u"就业", u"职教", u"科学", u"配套", u"护理", u"养殖", u"验配", u"修配", u"新闻", u"会展", u"育种", u"农资", u"物业", u"实业",
                   u"活动", u"清洁", u"体育", u"展示", u"用品", u"财金", u"检验", u"促进", u"维护", u"彩印", u"体检", u"汽贸", u"家私", u"急救",
                   u"机电", u"工贸", u"装饰", u"矫形", u"保健", u"海事", u"施工", u"器械", u"育苗"]
# 世界
SUFFIX_SHIJIE = [u"大"]
# 店
SUFFIX_DIAN = [u"书", u"商", u"专卖", u"电器", u"酒", u"电脑", u"专营", u"用品", u"家具", u"美容", u"阳市", u"饭", u"配件", u"服务", u"售商",
               u"批发", u"种子", u"托车", u"灯具", u"窗帘", u"家俱", u"雅天", u"加工"]
# 队:
SUFFIX_DUI = [u"质大", u"放映", u"察总", u"调查", u"法总", u"施工", u"查总", u"地质", u"测量", u"察支", u"程总", u"探大", u"路支", u"工程", u"测绘",
              u"设计", u"绘大", u"探矿", u"钻井", u"打井", u"局四", u"勘查", u"洁大", u"局二", u"工总", u"程大", u"机井", u"局一", u"抢险"]
# 馆:
SUFFIX_GUAN = [u"图书", u"科技", u"迎宾", u"园宾", u"技术", u"寓宾", u"泉宾", u"天宾", u"阳宾", u"滨宾", u"岛宾", u"谊宾", u"中宾", u"心宾", u"地宾",
               u"博物"]
# 汽贸:
SUFFIX_QIMAO = []
# 场
SUFFIX_CHANG_ = [u"商", u"广", u"农", u"市", u"猪", u"种", u"苗", u"林", u"工", u"卖", u"渔", u"菜", u"石", u"煤", u"砂", u"机", u"养殖",
                 u"种植", u"苗圃", u"园艺", u"繁育", u"苗木", u"花木", u"试验", u"繁殖", u"实验", u"停车", u"花卉", u"耕牛"]
# 基地
SUFFIX_JIDI = []
# 行
SUFFIX_HANG = [u"商", u"琴", u"支", u"器", u"分", u"车"]
# 集团
SUFFIX_JITUAN = [u"影视", u"建工", u"电缆", u"工程", u"实业", u"企业", u"泵业", u"柏泰", u"装饰", u"网架", u"电信", u"联丰", u"产业", u"建设",
                 u"环宇", u"六建", u"锅炉", u"软件", u"贸易", u"报业", u"兰天", u"发展", u"康奈", u"重工", u"科技", u"出版", u"机械", u"试金",
                 u"设备", u"电子"]
# 城
SUFFIX_CHENG = [u"电器", u"音像", u"家具", u"家私", u"手机", u"商", u"灯饰", u"电脑", u"装饰", u"汽车", u"家电", u"数码", u"美容", u"电子", u"家俱",
                u"器乐", u"傢俬", u"家俬", u"炊具", u"钢琴", u"文化", u"科技", u"隆星", u"乐书", u"家饰", u"同书", u"航天", u"批发", u"餐具", u"电话"]
# 会
SUFFIX_HUI = [u"协", u"联合", u"工", u"十字", u"省分", u"研究", u"爱国", u"学", u"管委", u"促进"]
# 社
SUFFIX_SHE = [u"合作", u"出版", u"服务", u"美术", u"旅行", u"报", u"联合", u"信息", u"作联", u"分", u"教育", u"杂志", u"供销", u"广告", u"总",
              u"商", u"印刷", u"图片", u"工艺", u"装饰", u"书"]
# 站
SUFFIX_ZHAN = [u"监测", u"供应", u"总", u"代办", u"推广", u"监督", u"服务", u"管理", u"畜牧", u"中心", u"维修", u"试验",
               u"修理", u"改良", u"工作", u"供精", u"公牛", u"鉴定", u"勘测", u"林业", u"检测", u"环卫", u"接待", u"防疫", u"物资",
               u"批发", u"器材", u"加油", u"采供", u"记者", u"公猪", u"专卖", u"粮", u"装配", u"指导", u"配肥", u"培训",
               u"检验", u"回收", u"分", u"动力", u"网络", u"监理", u"水文"]
# 室
SUFFIX_SHI = [u"办公", u"设计", u"教", u"实验", u"工作", u"营销", u"研究", u"阅览"]
# 学校
SUFFIX_XUEXIAO = []
# 大学
SUFFIX_DAXUE = []

DICT_SUFFIX = {u"公司": SUFFIX_GONGSHI, u"厂": SUFFIX_CHANG, u"院": SUFFIX_YUAN, u"所": SUFFIX_SUO, u"部": SUFFIX_BU,
               u"处": SUFFIX_CHU, u"局": SUFFIX_JU, u"中心": SUFFIX_ZHONGXIN, u"店": SUFFIX_DIAN, u"队": SUFFIX_DUI,
               u"馆": SUFFIX_GUAN, u"场": SUFFIX_CHANG_, u"行": SUFFIX_HANG, u"集团": SUFFIX_JITUAN, u"世界": SUFFIX_SHIJIE,
               u"汽贸": SUFFIX_QIMAO, u"基地": SUFFIX_JIDI, u"城": SUFFIX_CHENG, u"会": SUFFIX_HUI, u"社": SUFFIX_SHE,
               u"站": SUFFIX_ZHAN, u"室": SUFFIX_SHI, u"学校": SUFFIX_XUEXIAO, u"大学": SUFFIX_DAXUE}


def is_company_name(text):
    if len(text) <= 4:
        return False
    suffix = text[-1:]
    suflen = 1
    if suffix not in DICT_SUFFIX:
        suffix = text[-2:]
        suflen = 2
    if suffix not in DICT_SUFFIX:
        return False
    fixs = DICT_SUFFIX[suffix]
    if len(fixs) == 0:  # 如果没有指明的前置描述词，认为是一个组织名
        return True
    for fix in fixs:
        t = len(fix)
        if text[-(t + suflen):-suflen] == fix:  # 如果是指明的一个前置描述词，认为是一个组织名
            return True
    return False


BID_TYPE = {u"废标公告": u"(?:废标|失败|流标|作废)(?:的|)(?:公告|公示|通知书|通知|通告|说明)",
            u"变更公告": u"(?:更正|变更|修改)(?:的|)(?:公告|公示|通知书|通知|通告|说明)",
            u"暂停公告": u"(?:暂停|中止)(?:的|)(?:公告|公示|通知书|通知|通告|说明)",
            u"延期公告": u"(?:延期|延长)(?:的|)(?:公告|公示|通知书|通知|通告|说明)",
            u"取消公告": u"(?:取消|终止)(?:的|)(?:公告|公示|通知书|通知|通告|说明)",
            u"补充公告": u"(?:补充)(?:的|)(?:公告|公示|通知书|通知|通告|说明)",
            u"澄清公告": u"(?:澄清)(?:的|)(?:公告|公示|通知书|通知|通告|说明)",}


def get_bid_type_by_title(title):
    """
    根据标题名判断公告类型
    :param title:
    :return:
    """
    for bid_type, pattern in BID_TYPE.items():
        if re.search(pattern, title) is not None:
            return bid_type
    return None


def split_text_by_strings(strings, text):
    """
    将text按strings里的字符串依次分段
    :param strings: list 用于分割的字符串，必须依次出现在原字符串中，可以为空
    :param text: str 待分割字符串
    :return: list 返回分段结果
    """
    if isinstance(text, str):
        text = unicode(text)

    result = []
    suffix_text = text
    count = 0
    for string in strings:
        ind = suffix_text.find(string)
        if ind >= 0:
            count += ind
            suffix_text = suffix_text[ind + len(string):]
            prefix_text = text[:count]
            pre = prefix_text[prefix_text.rfind("\n") + 1:]
            t = suffix_text.find("\n")
            if t >= 0:
                suf = suffix_text[:t]
            else:
                suf = suffix_text
            result.append((pre, suf))
            count += len(string)
        else:
            msg = "Call function split_text_by_strings error: " + \
                  "There is no substring '%s' in '%s', please check your inputs." % (string, text)
            raise Exception(msg)
    return result


def generate_matrix(shape, def_val):
    result = []
    if len(shape) == 0:
        return None
    if len(shape) == 1:
        return [def_val for i in range(shape[0])]
    for i in range(shape[0]):
        row = generate_matrix(shape[1:], 1)
        result.append(row)
    return result


def ones_matrix(shape):
    return generate_matrix(shape, 1)


def ones_matrix_like(mat):
    shape = []
    while isinstance(mat, list):
        shape.append(len(mat))
        mat = mat[0]
    return ones_matrix(shape)


def zeros_matrix(shape):
    return generate_matrix(shape, 0)


def zeros_matrix_like(mat):
    shape = []
    while isinstance(mat, list):
        shape.append(len(mat))
        mat = mat[0]
    return zeros_matrix(shape)


