# coding=utf-8
"""
author = jamon
"""

import random
from server.rpc_connection_manager import RpcConnectionManager
from share.ob_log import logger


def call_remote_service(node_name, message):
    """

    :param node_name: string, 节点名
    :param message: string, 待发送的消息
    :return:
    """
    return RpcConnectionManager().send_message(node_name, message)


def send_message(node_type, message):
    """
    向其他节点推送消息
    :param node_type: int, 节点类型
    :param message: string, 消息内容
    :return:
    """
    available_servers = []
    for name in RpcConnectionManager().type_dict.get(node_type, []):
        if 1 == RpcConnectionManager().conns[name]["status"]:
            available_servers.append(name)
    if not available_servers:
        logger.error("find not server to push!")
        return
    index = random.randint(0, len(available_servers)-1)
    call_remote_service(available_servers[index], message)
