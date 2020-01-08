# coding=utf-8
"""
author = jamon
"""

import asyncio
import random

from base.common_define import NodeType, ConnectionStatus
from base.global_object import GlobalObject
from rpc.connection_manager import RpcConnectionManager
from share.ob_log import logger


async def call_remote_service(node_name, command_id, message, src=None, to=None):
    """

    :param node_name: string, 节点名
    :param command_id: int
    :param message: string, 待发送的消息
    :param src: string, 消息来自哪里（一般来自src）
    :param to: string, 消息最终发往哪里，为空时则根据消息ID发送
    :return:
    """
    return await RpcConnectionManager().send_message(node_name, command_id, message, src=src, to=to)


async def find_available_node(next_node_type, to=None):
    """
    寻找一个可用的节点，如果没有，则异步等待直到找到为止
    :param next_node_type:
    :param to:
    :return:
    """
    while True:
        if to and to in RpcConnectionManager().conns.keys() and ConnectionStatus.ESTABLISHED == \
                RpcConnectionManager().conns[to]["status"]:
            # 如果明确传输的目标，且和目标节点有直接可用的rpc连接，则直接通过该连接发送消息；
            next_node = to
        else:
            if NodeType.ROUTE == next_node_type:
                # 选取一个可用的route节点
                next_node = RpcConnectionManager().get_available_connection(NodeType.ROUTE)
            else:
                next_node = RpcConnectionManager().get_available_connection(next_node_type)
                if not next_node:
                    # 如果没有可用的next_node_type类型对应的节点， 则转发往路由节点
                    next_node = RpcConnectionManager().get_available_connection(NodeType.ROUTE)
            if not next_node:
                logger.error("all route node dead!!!")
                await asyncio.sleep(1)
                continue
        return next_node


async def send_message(next_node_type, command_id, message, src=None, to=None):
    """
    向其他节点推送消息
    :param next_node_type: int, 接下来发往的节点类型
    :param command_id: int
    :param message: string, 消息内容
    :param src: string, 消息来自哪里（一般来自src）
    :param to: string, 消息最终发往哪里，为空时则根据消息ID发送
    :return:
    """
    if next_node_type == GlobalObject().type:
        # 参数错误，自己给自己发消息
        logger.error("send_message:", next_node_type, command_id, message, src, to)
        raise Exception()

    next_node = await find_available_node(next_node_type, to=to)
    print("send_message:", next_node)
    await call_remote_service(next_node, command_id, message, src=src, to=to)
