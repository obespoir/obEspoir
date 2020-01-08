# coding=utf-8
"""
author = jamon
"""

import asyncio
import ujson

from websockets.exceptions import ConnectionClosed

from share.singleton import Singleton
from share.ob_log import logger
from base.common_define import NodeType
from base.ob_protocol import DataException
from base.global_object import GlobalObject
from websocket.protocol import WebSocketProtocol
from websocket.route import webSocketRouteHandle
from websocket.manager import WebsocketConnectionManager
from rpc.push_lib import send_message


class WebsocketHandler(object, metaclass=Singleton):

    def __init__(self):
        self.protocol = WebSocketProtocol()

    async def websocket_handler(self, websocket, path):
        print(websocket.remote_address, path)
        while True:
            try:
                data = await asyncio.wait_for(websocket.recv(), timeout=GlobalObject().ws_timeout)
                logger.debug('websocket received {!r}'.format(data))
                while data:  # 解决TCP粘包问题
                    data = await self.protocol.process_data(data, websocket)
            except asyncio.TimeoutError:
                logger.info("{} connection timeout!".format(websocket.remote_address))
                await websocket.close()
            except ConnectionClosed as e:
                logger.info("{} connection lose ({}, {})".format(websocket.remote_address,e.code, e.reason))
                return 0
            except DataException as e:
                logger.info("data decrypt error!")
                await websocket.close()
                return 0


@webSocketRouteHandle
async def forward_0(command_id, data):
    """
    消息转发
    :param command_id: int
    :param data: json
    :return:
    """
    print("forward_0", command_id, data, type(data))
    if not isinstance(data, dict):
        try:
            data = ujson.loads(data)
            print("data type :", type(data))
        except Exception:
            logger.warn("param data parse error {}".format(data))
            return {}
    data.update({"message_id": command_id})
    next_node = None
    for node, route in GlobalObject().ws_route["special"].items():
        if command_id in route:
            next_node = node
            break

    if not next_node:
        for node, route in GlobalObject().ws_route["range"].items():
            if next_node:
                break
            for r in route:
                if r[0] <= command_id <= r[1]:
                    next_node = node
                    break
    print("next_node:", next_node)
    if not next_node:
        logger.info("can not find route node for message {}".format(command_id))
        return {}
    else:
        src = GlobalObject().id
        next_node = NodeType.get_type(next_node)
        return await send_message(next_node, command_id, data, src=src, to=None)

