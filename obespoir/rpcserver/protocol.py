# coding=utf-8
"""
author = jamon
"""

import asyncio
import struct
import ujson

from share.ob_log import logger
from share.encodeutil import AesEncoder
from base.ob_protocol import ObProtocol
from rpcserver.route import rpc_message_handle
from base.global_object import GlobalObject


class RpcProtocol(ObProtocol):
    """消息协议，包含消息处理"""

    def __init__(self):
        super().__init__()
        self.handfrt = "iii"  # (int, int, int)  -> (message_length, command_id, version)
        self.head_len = struct.calcsize(self.handfrt)
        self.identifier = 0

        self.encode_ins = AesEncoder(GlobalObject().rpc_password, encode_type=GlobalObject().rpc_encode_type)
        self.version = 0

        self._buffer = b""    # 数据缓冲buffer
        self._head = None     # 消息头, list,   [message_length, command_id, version]
        self.transport = None

    async def message_handle(self, command_id, version, data):
        """
        实际处理消息
        :param command_id:
        :param version:
        :param data:
        :return:
        """
        print("rpc protocol message_handle:", command_id, data)
        # result = await rpc_route.call_target(command_id, data)
        result = await rpc_message_handle(command_id, data)
        print("rpc result=", result)
        # self.transport.write(self.pack(result, command_id))
        # await RpcConnectionManager().send_message(command_id=command_id, data=self.pack(result, command_id))
        # self.transport.write(self.pack(result, command_id))

    def connection_made(self, transport):
        self.transport = transport
        # self.address = transport.get_extra_info('peername')
        address = transport.get_extra_info('peername')
        # RpcConnectionManager().store_connection(*address, self)
        logger.debug('connection accepted {}'.format(address))

    def data_received(self, data):
        logger.debug('rpcserver received {!r}'.format(data))
        super().data_received(data)

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


