# coding=utf-8
"""
author = jamon
"""

import asyncio
import traceback
import ujson

from functools import wraps
from share.ob_log import logger
from server.ob_service import rpc_service


class ObProtocol(asyncio.Protocol):
    """消息协议，包含消息处理"""

    def connection_made(self, transport):
        self.transport = transport
        self.address = transport.get_extra_info('peername')
        logger.debug('connection accepted')

    def data_received(self, data):
        logger.debug('received {!r}'.format(data))
        result = ""
        if not isinstance(data, dict):
            try:
                data = ujson.loads(data)
            except Exception as e:
                logger.warn("param error:{0}".format(data))
                return

        if data.get("message_id", 0):
            result = ujson.dumps({"code": 0, "desc": "error"})
        else:
            result = rpc_service.callTarget(data["message_id"], data)
        self.transport.write(result)

    def eof_received(self):
        logger.debug('received EOF')
        if self.transport.can_write_eof():
            self.transport.write_eof()

    def connection_lost(self, error):
        if error:
            logger.error('ERROR: {}'.format(error))
        else:
            logger.debug('closing')
        super().connection_lost(error)


