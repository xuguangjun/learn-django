# -*- coding: utf-8 -*-
import logging


logger = logging.getLogger(__name__)


def read_file_data(file):
    if file.size > 2000000:
        logger.error("file size too big: " + file.size)
    try:
        return file.read().decode("gbk")
    except UnicodeDecodeError, e:
        return file.read()


class VersionHelperClass:
    def __init__(self, version_object):
        self.dict = {}
        for v in version_object:
            self.dict[v.version_id] = v.version_name

    def get(self, key, default_value):
        return self.dict.get(key, default_value)
