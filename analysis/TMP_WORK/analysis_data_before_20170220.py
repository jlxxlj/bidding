# coding=utf-8
# author="Jianghua Zhao"


"""
对招投标公告文档进行解析，提取其中有用信息
"""

import os
import sys

par_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if par_dir not in sys.path:
    sys.path.append(par_dir)
from announce_analysis import *
from announce_analysis_result_save import announce_analysis_result_save

reload(sys)
sys.setdefaultencoding('utf-8')

logger = get_logger(__file__)


provinces = [
    # "tai_wan", "ao_men", "xiang_gang",
    # "ning_xia", "guang_xi", "xi_zhang", "xing_jiang", "nei_meng_gu", "hai_nan",
    # "guang_dong", "yun_nan", "gui_zhou", "qing_hai", "gan_su",
    # "si_chuan", "jiang_xi", "fu_jian", "an_hui", "zhe_jiang",
    # "jiang_su", "ji_lin", "liao_ning", "hei_long_jiang", "hu_nan",
    # "hu_bei", "shan_xi-", "shan_dong", "shan_xi_", "he_nan",
    # "he_bei", "shang_hai", "chong_qing", "tian_jin", "bei_jing",
    # "quan_guo"
]


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
    s3util = aws_s3_sc.S3Util()
    s3_client = aws_s3_sc.get_aws_client("s3")

    paginator = s3_client.get_paginator('list_objects')

    try:
        for pvc in provinces:
            response_iterator = paginator.paginate(
                Bucket='bidding',
                Prefix='source/' + pvc,
            )

            ed_date = datetime.datetime(year=2017, month=2, day=20)
            for page in response_iterator:
                for item in page.get("Contents", []):
                    object_key = item["Key"]

                    # 验证object_key
                    if reg_key.match(object_key) is None:
                        continue

                    # 从s3上读数据
                    logger.info("process: " + object_key)
                    try:
                        obj = s3util.select(table="bidding", condition={}, file_name=object_key)
                        s3_data = json.loads(obj["Body"].read())
                    except KeyboardInterrupt as e:
                        raise e
                    except Exception as e:
                        logger.exception(e)
                        continue

                    publish_date = extract_first_date(s3_data.get(PUBLISHED_TS))
                    if not publish_date:
                        continue
                    if publish_date > ed_date:
                        logger.info("Announce's publish date is after %s and skip analysis." % ed_date.strftime("%Y-%m-%d"))
                        continue

                    # 分析数据
                    try:
                        announce_data = analysis(s3_data)
                    except Exception as e:
                        logger.exception(e)
                        new_name = "parse_error/" + urllib.urlencode({"name": object_key})[5:]
                        s3util.insert(table="bidding", data=s3_data, file_name=new_name)
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

        logger.info("work done.")
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    main()
