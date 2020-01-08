# coding=utf-8
"""
author = jamon
"""

import asyncio
import ujson
import struct

from base.global_object import GlobalObject
from rpc.connection_manager import RpcConnectionManager
from share.encodeutil import AesEncoder
from share.ob_log import logger


class RpcPushProtocol(asyncio.Protocol):

    def __init__(self):
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
        super().__init__()

    def pack(self, data, command_id, src=None, to=None):
        """
        打包消息， 用於傳輸
        :param data:  傳輸數據
        :param command_id:  消息ID
        :return: bytes
        """
        info = {"src": src, "to": to, "data": data}
        data = self.encode_ins.encode(ujson.dumps(data))
        # data = "%s" % data
        length = data.__len__() + self.head_len
        head = struct.pack(self.handfrt, length, command_id, self.version)
        return head + data

    async def send_message(self, command_id, message, src, to=None):
        data = self.pack(message, command_id, src, to)
        print("rpc_push send_message:", data, type(data))
        self.transport.write(data)

    def connection_made(self, transport):
        self.transport = transport
        address = transport.get_extra_info('peername')
        self.host, self.port = address
        RpcConnectionManager().store_connection(*address, self)
        logger.debug(
            'connected to {} port {}'.format(*address)
        )

    def data_received(self, data):
        logger.debug('rpc_push received {!r}'.format(data))

    def eof_received(self):
        logger.debug('rpc_push received EOF')
        if self.transport and self.transport.can_write_eof():
            self.transport.write_eof()
        RpcConnectionManager().lost_connection(self.host, self.port)

    def connnection_lost(self, exc):
        logger.debug('server closed connection')
        RpcConnectionManager().lost_connection(self.host, self.port)
        super(RpcPushProtocol, self).connection_lost(exc)


