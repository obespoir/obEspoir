# coding=utf-8
"""
author = jamon
"""

import asyncio
from websockets.exceptions import ConnectionClosed

from obespoir.base.ob_route import ObRoute
from obespoir.share.ob_log import logger
from obespoir.share.singleton import Singleton
from obespoir.base.ob_protocol import DataException
from obespoir.base.global_object import GlobalObject


class WebSocketRoute(ObRoute):

    def get_target(self, targetKey):
        """Get a target from the service by name."""
        self._lock.acquire()
        try:
            target = self._targets.get(targetKey, None)
            if not target:
                target = self._targets.get(0, None)
        finally:
            self._lock.release()
        return target


websocket_route = WebSocketRoute()


def webSocketRouteHandle(target):
    websocket_route.map_target(target)


class WebsocketHandler(object, metaclass=Singleton):

    def __init__(self):
        pass

    async def websocket_handler(self, websocket, path):
        logger.debug("websocket_handler: {}, {}".format(websocket.remote_address, path))
        while True:
            try:
                data = await asyncio.wait_for(websocket.recv(), timeout=GlobalObject().ws_timeout)
                logger.debug('websocketserver received {!r}'.format(data))
                # await websocket.send("hello")
                while data:  # 解决TCP粘包问题
                    data = await websocket.process_data(data, websocket)
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