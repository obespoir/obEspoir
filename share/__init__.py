# coding=utf-8
"""
author = jamon
"""


import sys


def get_root_dir():
    """
    获取项目根目录
    :return:
    """
    base_path = sys._getframe().f_code.co_filename
    result = base_path.rsplit('/', 2)
    if 1 == len(result):  # window平台上路径使用的"\\"
        result = base_path.rsplit("\\", 2)

    return result[0]

