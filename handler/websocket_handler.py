# coding=utf-8
"""
author = jamon
"""

from websockets.exceptions import ConnectionClosed

from handler.data_pack import DataProtocol
from share.singleton import Singleton
from share.ob_log import logger


class WebsocketHandler(object):

    __metaclass__ = Singleton

    def __init__(self):
        self.protocol = DataProtocol()

    async def websocket_handler(self, websocket, path):
        print(websocket.remote_address, path)
        while True:
            try:
                recv_text = await websocket.recv()
                response_text = f"your submit context: {recv_text}"
                await websocket.send(response_text)
                await websocket.close()
                print("bbbbbbbbbbb")
            except ConnectionClosed as e:
                logger.info("{} connection lose ({}, {})".format(websocket.remote_address,e.code, e.reason))
                return 0

