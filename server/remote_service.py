# coding=utf-8
"""
author = jamon
"""

import random
from server.rpc_connection_manager import RpcConnectionManager
from share.ob_log import logger


async def call_remote_service(node_name, command_id, message):
    """

    :param node_name: string, 节点名
    :param command_id: int
    :param message: string, 待发送的消息
    :return:
    """
    return await RpcConnectionManager().send_message(node_name, command_id, message)


async def send_message(node_type, command_id, message):
    """
    向其他节点推送消息
    :param node_type: int, 节点类型
    :param command_id: int
    :param message: string, 消息内容
    :return:
    """
    available_servers = []
    for name in RpcConnectionManager().type_dict.get(node_type, []):
        if name in RpcConnectionManager().conns and 1 == RpcConnectionManager().conns[name]["status"]:
            available_servers.append(name)
    if not available_servers:
        print("sssserver:", available_servers)
        logger.error("find not server to push!")
        return
    index = random.randint(0, len(available_servers)-1)
    print("send_message:", available_servers, index)
    await call_remote_service(available_servers[index], command_id, message)
