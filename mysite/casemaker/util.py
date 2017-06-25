# -*- coding: utf-8 -*-
import logging


logger = logging.getLogger(__name__)
CONFIG_STATE_INITIAL = 1  # 配置文件上传成功
CONFIG_STATE_DONE = 2  # 配置文件生成case成功，可此时可以下载case
CONFIG_STATE_DOING = 3  # 配置文件正在生成case，中间状态
TEST_CASE_GENERATE = False  # 是否真正生成case，主要用于测试
ITEM_NUM_PER_PAGE = 15  # 默认每页展示20条数据
GET_PAGE_DOWN = 1  # 分页中，查看下一页
GET_PAGE_UP = 2  # 分页中，查看上一页
GET_PAGE_CURRENT = 3  # 分页中，查看本页


def read_file_data(file):
    if file.size > 2000000:
        logger.error("file size too big: " + file.size)
    try:
        return file.read().decode("utf-8")
    except UnicodeDecodeError, e:
        return ""

