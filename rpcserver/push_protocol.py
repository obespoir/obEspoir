# coding=utf-8
"""
author = jamon
"""

import asyncio
import ujson
import struct

from base.common_define import ConnectionStatus
from base.global_object import GlobalObject
from base.ob_protocol import ObProtocol
from rpcserver.connection_manager import RpcConnectionManager
from rpcserver.route import rpc_message_handle
from share.encodeutil import AesEncoder
from share.ob_log import logger


class RpcPushProtocol(ObProtocol):

    def __init__(self):
        super().__init__()
        self.host = None
        self.port = None
        self.handfrt = "iii"  # (int, int, int)  -> (message_length, command_id, version)
        self.head_len = struct.calcsize(self.handfrt)
        self.identifier = 0

        self.encode_ins = AesEncoder(GlobalObject().rpc_password, encode_type=GlobalObject().rpc_encode_type)
        self.version = 0

        self._buffer = b""    # 数据缓冲buffer
        self._head = None     # 消息头, list,   [message_length, command_id, version]
        self.transport = None

    async def send_message(self, command_id, message, session_id, to=None):
        print("rpc push:", message, type(message))
        data = self.pack(message, command_id, session_id, to)
        print("rpc_push send_message:", data, type(data))
        self.transport.write(data)

    async def message_handle(self, command_id, version, data):
        """
        实际处理消息
        :param command_id:
        :param version:
        :param data:
        :return:
        """
        print("rpc push receive response message_handle:", command_id, data)
        # result = await rpc_route.call_target(command_id, data)
        result = await rpc_message_handle(command_id, data)
        print("rpc result=", result)
        # self.transport.write(self.pack(result, command_id))

    def connection_made(self, transport):
        self.transport = transport
        address = transport.get_extra_info('peername')
        self.host, self.port = address
        RpcConnectionManager().store_connection(*address, self, status=ConnectionStatus.ESTABLISHED)
        logger.debug(
            'connected to {} port {}'.format(*address)
        )

    def data_received(self, data):
        logger.debug('rpc_push received response {!r}'.format(data))
        super().data_received(data)

    def eof_received(self):
        logger.debug('rpc_push received EOF')
        if self.transport and self.transport.can_write_eof():
            self.transport.write_eof()
        RpcConnectionManager().lost_connection(self.host, self.port)

    def connnection_lost(self, exc):
        logger.debug('server closed connection')
        RpcConnectionManager().lost_connection(self.host, self.port)
        super(RpcPushProtocol, self).connection_lost(exc)


