# coding=utf-8
"""
author = jamon
"""

import ujson

from base.ob_handler import RegisterEvent
from base.common_define import NodeType
from base.global_object import GlobalObject
from rpcserver.push_lib import push_message
from share.ob_log import logger
from websocketserver.manager import WebsocketConnectionManager


async def call_target(command_id, data, session_id):
    """
    调用注册的消息处理
    :param command_id:
    :param data:
    :param session_id:
    :return:
    """
    obj = RegisterEvent.events.get(command_id, None)
    if not obj:
        logger.error("command_id {} not register!".format(command_id))
        return
    handler = obj.get("handler")(data, command_id, session_id)
    ret = await handler.execute()
    if obj.get("need_return"):
        to, _ = session_id.split("_")
        await push_message(None, command_id, ret, session_id, to)


async def rpc_message_handle(command_id, data):
    """
    接收到rpc消息处理
    :param command_id: int, 消息ID
    :param data: dict, 消息内容
    :return:
    """
    if not isinstance(data, dict):
        data = data.decode("utf-8") if isinstance(data, bytes) else data
        data = ujson.loads(data)
    print("rpc_message_handle:", command_id, data, type(data), GlobalObject().id)
    session_id = data.get("src", None)
    to = data.get("to", None)
    info = data.get("data", {})
    if to:
        if to != GlobalObject().id:
            return await forwarding_next(command_id, info, session_id, to)
        else:
            return await local_handle(command_id, data, session_id)
    else:
        if GlobalObject().rpc_route:   # 配置了路由信息（一般只有route类型节点才会配置）
            next_node = -1
            for node, route in GlobalObject().rpc_route.get("special", {}).items():
                if command_id in route:
                    next_node = node
                    break

            if not next_node:
                for node, route in GlobalObject().rpc_route.get("range", {}).items():
                    if next_node:
                        break
                    for r in route:
                        if r[0] <= command_id <= r[1]:
                            next_node = node
                            break
            print("bbbbbb:", next_node, GlobalObject().type, command_id, GlobalObject().rpc_route)
            if -1 == next_node:
                next_node = NodeType.ROUTE
            if next_node == GlobalObject().type:
                return await local_handle(command_id, data, session_id)
            else:
                return await push_message(next_node, command_id, data, session_id, to)
        else:   # 没有路由信息，则默认为本地处理
            return await local_handle(command_id, data, session_id)


async def forwarding_next(command_id, data, session_id, to):
    """
    有明确目标，向其他节点转发
    :param command_id:
    :param data:
    :param session_id:
    :param to:
    :return:None
    """
    return await push_message(None, command_id, data, session_id, to)


async def local_handle(command_id, data, session_id):
    """
    无需转发, 本节点处理的消息
    :param command_id:
    :param data:
    :param session_id:
    :return: None
    """
    if NodeType.PROXY == GlobalObject().type:
        # proxy类型节点收到rpc消息后会通过websocket推送给客户端
        seq = int(session_id.split("_")[-1])
        client = WebsocketConnectionManager().get_websocket(seq)
        if not isinstance(data, str):
            data = ujson.dumps(data)
        print("cccccc:", data, command_id, client)
        await client.send_message(data, command_id)
        return
    else:
        await call_target(command_id, data, session_id=session_id)

