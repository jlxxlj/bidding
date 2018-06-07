# coding=utf-8
# author="Jianghua Zhao"


"""
对招投标公告文档进行解析，提取其中有用信息
"""
import sys
import re
import json
import urllib

from scpy.logger import get_logger

from db import aws_s3_sc

from scpy.date_extractor import extract_first_date
from html_purify import purify_html
import html_convert_to_dict
import html_dict_analysis

from announce_attributes import *
from announce_analysis_result_key_map import announce_keys_map, result_keys_map
from announce_analysis_result_save import announce_analysis_result_save

reload(sys)
sys.setdefaultencoding('utf-8')

logger = get_logger(__file__)


def complete_key_map(key_map, data):
    """
    完成原始字典数据到结果的映射
    :param key_map:  字段映射表
    :param data:  原始字典数据
    :return:  结果字典数据
    """
    result = {}
    for key, map_key in key_map.items():
        if not map_key:
            continue
        if not isinstance(map_key, (tuple, list)):
            map_key = [map_key]

        value = None
        for cad_key in map_key:
            t = data
            while t and isinstance(cad_key, dict):
                t = t.get(cad_key.keys()[0])
                cad_key = cad_key.values()[0]
            if t:
                value = t.get(cad_key)
                if value:
                    break
        if value:
            result[key] = value
    return result


def initial_analysis_env():
    from obtain_element_info import clear_cache
    clear_cache()


def analysis(announce_item):
    """
    解析公告文本
    :param announce_item:
    :return:
    """
    # announce_data = announce_data_template()

    initial_analysis_env()

    content = announce_item.get("content")
    cont = purify_html(content)
    # print cont
    doc = html_convert_to_dict.analysis_html(cont)
    print doc
    bidding_item = html_dict_analysis.analysis_announce_doc(doc, pre_info=announce_item, src_html=content)

    announce_data = complete_key_map(announce_keys_map, bidding_item)

    segments = bidding_item.get(SEGMENTS)
    participator = []
    for seg in segments:
        seg_name = seg.get(SEGMENT_NAME)

        winner = seg.get(WINNER)
        if winner:
            win = complete_key_map(result_keys_map, winner)
            if not win.get("role_name"):
                win["role_name"] = u"中标人"
            if seg_name:
                win["segment_name"] = seg_name
            win["role_type"] = "winner"
            participator.append(win)

        candidates = seg.get(CANDIDATES)
        for candidate in candidates:
            cand = complete_key_map(result_keys_map, candidate)
            if not cand.get("role_name"):
                cand["role_name"] = u"中标候选人"
            if seg_name:
                cand["segment_name"] = seg_name
            cand["role_type"] = "candidate"
            participator.append(cand)

    # 去掉重复的,没有意义的结果
    announce_data["participator"] = []
    for i, part in enumerate(participator):
        sig = True
        for j, part_ in enumerate(announce_data["participator"]):
            if part_.get("winning_company") == part.get("winning_company") and \
                            part_.get("role_type") == part.get("role_type"):
                if part_.get("winning_amount") is None and part.get("winning_amount"):
                    announce_data["participator"][j] = part
                    sig = False
                elif part_.get("winning_amount") and part.get("winning_amount") is None:
                    sig = False
                elif part_.get("winning_amount") == part.get("winning_amount"):
                    if not part.get("candidate_rank") or part_.get("segment_name") == part.get("segment_name"):
                        sig = False
        if sig:
            announce_data["participator"].append(part)

    print "=" * 80
    for i, win in enumerate(announce_data["participator"]):
        print "role:{0}, company:{1}, currency:{2}, amount:{3}, unit:{4}, rank: {5}".format(
            win.get("role_name", ""),
            win.get("winning_company"),
            win.get("currency"),
            win.get("winning_amount"),
            win.get("unit"),
            win.get("candidate_rank", "")
        )

    return announce_data


# 定时从s3中读取最新的数据分析并存库
def main():
    """
    公告解析算法主循环
    :return:
    """
    # 验证object_key
    region_code = u"|".join(BID_REGION_CODE_TABLE.values())
    reg_key = re.compile(u"^source/(?:%s)/.*/\d{4}/\d{1,2}/\d{1,2}/.*\.json" % region_code)

    # Get the service resource
    sqs = aws_s3_sc.get_aws_service("sqs")
    s3util = aws_s3_sc.S3Util()

    # Get the queue. This returns an SQS.Queue instance
    queue = sqs.get_queue_by_name(QueueName='bidding_sqs')

    sleep_second = 1
    st_date = datetime.datetime(year=2016, month=9, day=1)

    while True:
        try:
            res = queue.receive_messages()
            if len(res) == 0:
                sleep_second = min(60, sleep_second * 2)
                logger.info("There is no more message and processor will sleep for %s seconds" % sleep_second)
                time.sleep(sleep_second)
                continue
            else:
                sleep_second = 1

            for msg in res:
                msg_body = json.loads(msg.body)
                object_key = msg_body["Records"][0]["s3"]["object"]["key"]
                object_key = urllib.unquote(object_key)

                # 验证object_key
                if reg_key.match(object_key) is None:
                    msg.delete()
                    continue

                # 从s3上读数据
                logger.info("announce s3 key: " + object_key)
                try:
                    obj = s3util.select(table="bidding", condition={}, file_name=object_key)
                    s3_data = json.loads(obj["Body"].read())
                except KeyboardInterrupt as e:
                    raise e
                except Exception as e:
                    logger.exception(e)
                    msg.delete()
                    continue

                publish_date = extract_first_date(s3_data.get(PUBLISHED_TS))
                if not publish_date:
                    continue
                if publish_date < st_date:
                    logger.info(
                        "Announce's publish date is before %s and skip analysis." % st_date.strftime("%Y-%m-%d"))
                    msg.delete()
                    continue

                # 分析数据
                try:
                    announce_data = analysis(s3_data)
                except Exception as e:
                    logger.exception(e)
                    new_name = "parse_error/" + urllib.urlencode({"name": object_key})[5:]
                    s3util.insert(table="bidding", data=s3_data, file_name=new_name)
                    msg.delete()
                    continue

                # 存库
                try:
                    content_source = "s3:bidding:" + object_key
                    announce_analysis_result_save(announce_data, content_source)
                except Exception as e:
                    logger.exception(e)
                    new_name = "save_error/" + datetime.datetime.now().strftime("%Y/%m/")
                    new_name += urllib.urlencode({"name": object_key})[5:]
                    s3util.insert(table="bidding", data=s3_data, file_name=new_name)
                # 删除消息
                msg.delete()

        except Exception as e:
            logger.exception(e)
            break


def test_fun():
    object_key = "source/chong_qing/www.cqggzy.com/2017/01/05/http%3A%2F%2Fwww.cqggzy.com%2Fxxhz%2F014001%2F014001004%2F20170105%2F0be9c862-5ccc-4382-9e20-27c508bbbcca.html.json"
    s3util = aws_s3_sc.S3Util()

    # 从s3上读数据
    obj = s3util.select(table="bidding", condition={}, file_name=object_key)
    s3_data = json.loads(obj["Body"].read())
    print "\n", object_key
    # 分析数据
    announce_data = analysis(s3_data)
    # 存库
    # result_name = object_key.replace("source", "analysis_result", 1)
    # s3util.insert(table="bidding", data=bidding_item, file_name=result_name)
    announce_analysis_result_save(announce_data, object_key)


def check_monitor_process_number():
    from config.config import CHECK_MONITOR_PROCESS_NUMBER, MAX_MONITOR_PROCESS_NUMBER
    import commands
    import re
    if CHECK_MONITOR_PROCESS_NUMBER:
        out = commands.getoutput("ps -aux | grep announce_analysis.py")
        process_number = len(re.findall("python announce_analysis.py", out))
        if process_number >= MAX_MONITOR_PROCESS_NUMBER:
            logger.info(
                "There are already %s monitor process(es), this process will exit." % MAX_MONITOR_PROCESS_NUMBER)
            sys.exit(0)


if __name__ == "__main__":
    check_monitor_process_number()
    main()
    # test_fun()
