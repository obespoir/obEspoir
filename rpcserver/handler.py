# coding=utf-8
"""
author = jamon
"""

import ujson

from rpcserver.route import rpcRouteHandle
from share.ob_log import logger


@rpcRouteHandle
def login_1000(command_id, data):
    """

    :param command_id: int
    :param data:
    :return:
    """
    logger.info("login_1000:{}_{}".format(command_id, data))
    return ujson.dumps({"code": 200})

