# coding=utf-8
"""
author = jamon
"""

import struct

from share.encodeutil import AesEncoder
from server.ob_protocol import ObProtocol, DataException
from server.ob_service import websocket_service
from server.global_object import GlobalObject


class WebSocketProtocol(ObProtocol):
    """消息协议，包含消息处理"""

    def __init__(self):
        self.handfrt = "iii"  # (int, int, int)  -> (message_length, command_id, version)
        self.head_len = struct.calcsize(self.handfrt)
        self.identifier = 0

        self.encode_ins = AesEncoder(GlobalObject().rpc_password, encode_type=GlobalObject().rpc_encode_type)
        self.version = 0

        self._buffer = b""    # 数据缓冲buffer
        self._head = None     # 消息头, list,   [message_length, command_id, version]
        self.transport = None
        super().__init__()

    def pack(self, data, command_id):
        """
        打包消息， 用於傳輸
        :param data:  傳輸數據
        :param command_id:  消息ID
        :return: bytes
        """
        data = self.encode_ins.encode(data)
        length = data.__len__() + self.head_len
        head = struct.pack(self.handfrt, length, command_id, self.version)
        return head + data

    async def process_data(self, data, websocket):
        if isinstance(data, str):
            data = bytes(data, encoding='utf8')
        self._buffer += data
        _buffer = None
        if self._head is None:
            if len(self._buffer) < self.head_len:
                return

            self._head = struct.unpack(self.handfrt, self._buffer[:self.head_len])      # 包头
            self._buffer = self._buffer[self.head_len:]
        content_len = self._head[0] - self.head_len
        if len(self._buffer) >= content_len:
            data = self.encode_ins.decode(self._buffer[:content_len])   # 解密
            if not data:
                raise DataException()
            await self.message_handle(self._head[1], self._head[2], data, websocket)

            _buffer = self._buffer[content_len:]
            self._buffer = b""
            self._head = None
        return _buffer

    async def message_handle(self, command_id, version, data, websocket):
        """
        实际处理消息
        :param command_id:
        :param version:
        :param data:
        :return:
        """
        print("message_handle:", data)
        result = await websocket_service.call_target(command_id, data)
        if result:
            websocket.send(self.pack(result, command_id).decode("utf8"))
