# coding=utf-8
"""
author = jamon
"""

import asyncio

from server.rpc_connection_manager import RpcConnectionManager
from share.ob_log import logger


class RpcPushProtocol(asyncio.Protocol):

    def __init__(self):
        self.host = None
        self.port = None

    def connection_made(self, transport):
        address = transport.get_extra_info('peername')
        self.host, self.port = address
        RpcConnectionManager().store_connection(*address, transport)
        logger.debug(
            'connecting to {} port {}'.format(*address)
        )

    def data_received(self, data):
        logger.debug('received {!r}'.format(data))

    def eof_received(self):
        logger.debug('received EOF')
        if self.transport.can_write_eof():
            self.transport.write_eof()
        self.transport.close()

    def connnection_lost(self, exc):
        logger.debug('server closed connection')
        self.transport.close()
        super().connectiong_lost(exc)


