# coding=utf-8
"""
author = jamon
"""

import asyncio

from websockets.exceptions import ConnectionClosed

from share.singleton import Singleton
from share.ob_log import logger
from server.ob_protocol import DataException
from server.ob_service import WebSocketServiceHandle
from server.global_object import GlobalObject
from server.ws_protocol import WebSocketProtocol
from server.remote_service import call_remote_service


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
                    data = self.protocol.process_data(data)
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


@WebSocketServiceHandle
def forward_0(command_id, data):
    """
    消息转发
    :param command_id:
    :param data:
    :return:
    """
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
                if command_id >= r[0] and command_id<=r[1]:
                    next_node = node
                    break

    if not next_node:
        logger.info("can not find route node for message {}".format(command_id))
        return
    else:
        return call_remote_service(next_node, data)

