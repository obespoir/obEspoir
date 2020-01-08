# coding=utf-8
"""
author = jamon
"""

import ujson

from base.global_object import GlobalObject
from rpc.connection_manager import RpcConnectionManager
from rpc.push_lib import send_message
from rpc.route import rpcRouteHandle, rpc_route
from share.ob_log import logger


async def rpc_message_handle(command_id, data):
    """
    接收到rpc消息处理
    :param command_id: int, 消息ID
    :param data: dict, 消息内容
    :return:
    """
    if not isinstance(data, dict):
        data = ujson.loads(data)
    src = data.get("src", None)
    to = data.get("to", None)
    info = data.get(data, {})
    if to and to != GlobalObject().id:
        await forwarding_next(command_id, info, src, to)
    else:
        await local_handle(command_id, data, src)


async def forwarding_next(command_id, data, src, to):
    """
    有明确目标，向其他节点转发
    :param command_id:
    :param data:
    :param src:
    :param to:
    :return:
    """
    return await send_message(None, command_id, data, src, to)


async def local_handle(command_id, data, src):
    """
    无需转啊, 本节点处理的消息
    :param command_id:
    :param data:
    :param src:
    :return:
    """
    return await rpc_route.call_target(command_id, data)


@rpcRouteHandle
def login_1000(command_id, data):
    """

    :param command_id: int
    :param data:
    :return:
    """
    logger.info("login_1000:{}_{}".format(command_id, data))
    return ujson.dumps({"code": 200})

