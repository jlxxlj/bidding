# coding=utf-8
# author="Jianghua Zhao"


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


# 定时从s3中读取最新的数据分析并存库
def main():
    """
    公告解析算法主循环
    :return:
    """
    # Get the service resource
    s3util = aws_s3_sc.S3Util()
    s3_client = aws_s3_sc.get_aws_client("s3")

    paginator = s3_client.get_paginator('list_objects')

    try:
        prefixes = ["parse_error/", "save_error/"]
        for pref in prefixes:
            response_iterator = paginator.paginate(
                Bucket='bidding',
                Prefix=pref,
            )

            for page in response_iterator:
                for item in page.get("Contents", []):
                    object_key = item["Key"]
                    src_object_key = re.sub(u"^.*?/(?=source)", u"", object_key)
                    src_object_key = urllib.unquote(src_object_key)

                    # 从s3上读数据
                    logger.info("process: " + object_key)
                    try:
                        obj = s3util.select(table="bidding", condition={}, file_name=src_object_key)
                        s3_data = json.loads(obj["Body"].read())
                    except KeyboardInterrupt as e:
                        raise e
                    except Exception as e:
                        logger.exception(e)
                        continue

                    publish_date = extract_first_date(s3_data.get(PUBLISHED_TS))
                    if not publish_date:
                        continue

                    # 分析数据
                    try:
                        announce_data = analysis(s3_data)
                    except Exception as e:
                        logger.exception(e)
                        continue
                    # 存库
                    try:
                        content_source = "s3:bidding:" + src_object_key
                        announce_analysis_result_save(announce_data, content_source)
                    except Exception as e:
                        logger.exception(e)
                        continue

                    s3util.delete(table="bidding", condition={}, file_name=object_key)

        logger.info("work done.")
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    main()
