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
            'connected to {} port {}'.format(*address)
        )

    def data_received(self, data):
        logger.debug('received {!r}'.format(data))

    def eof_received(self):
        logger.debug('received EOF')
        transport = RpcConnectionManager().get_transport(self.host, self.port)
        if transport and transport.can_write_eof():
            transport.write_eof()
        RpcConnectionManager().lost_connection(self.host, self.port)

    def connnection_lost(self, exc):
        logger.debug('server closed connection')
        RpcConnectionManager().lost_connection(self.host, self.port)
        super().connectiong_lost(exc)


