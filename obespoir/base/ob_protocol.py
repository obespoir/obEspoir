# coding=utf-8
"""
author = jamon
"""

import asyncio
import struct
import ujson

from obespoir.base.global_object import GlobalObject
from obespoir.share.ob_log import logger


class DataException(Exception):

    pass
    

class ObProtocol(asyncio.Protocol):
    """消息协议，包含消息处理"""

    def __init__(self):
        self.handfrt = "iii"  # (int, int, int)  -> (message_length, command_id, version)
        self.head_len = struct.calcsize(self.handfrt)
        self.encode_ins = None
        self.version = 0

        self._buffer = b""    # 数据缓冲buffer
        self._head = None     # 消息头

    def pack(self, data, command_id, session_id=None, to=None):
        """
        打包消息， 用於傳輸
        :param data:  傳輸數據
        :param command_id:  消息ID
        :return:
        """
        data = ujson.dumps({"src": session_id, "to": to, "data": data})
        data = self.encode_ins.encode(data)
        length = data.__len__() + self.head_len
        head = struct.pack(self.handfrt, length, command_id, self.version)
        return head + data

    def process_data(self, data):
        if isinstance(data, str):
            data = bytes(data, encoding='utf8')
        self._buffer += data
        _buffer = None
        if self._head is None:
            if len(self._buffer) < self.head_len:
                return

            self._head = struct.unpack(self.handfrt, self._buffer[:self.head_len])  # 包头
            self._buffer = self._buffer[self.head_len:]
        content_len = self._head[0] - self.head_len
        logger.info("here22222: {}".format([content_len, len(self._buffer), self._head]))
        if len(self._buffer) >= content_len:
            data = self.encode_ins.decode(self._buffer[:content_len])  # 解密
            if not data:
                raise DataException()
            logger.info("hhhhhhhhhhhhhhhhhhh {}, {}".format(len(self._buffer), self._buffer[:100]))
            asyncio.ensure_future(self.message_handle(self._head[1], self._head[2], data), loop=GlobalObject().loop)

            _buffer = self._buffer[content_len:]
            self._buffer = b""
            self._head = None
        logger.info("here3333333: {}".format([len(_buffer), len(self._buffer), self._buffer[:100]]))
        return _buffer

    async def message_handle(self, command_id, version, data):
        """
        实际处理消息
        :param command_id:
        :param version:
        :param data:
        :return:
        """
        raise NotImplementedError

    def connection_made(self, transport):
        super(ObProtocol, self).connection_made(transport)

    def data_received(self, data):
        while data:     # 解决TCP粘包问题
            data = self.process_data(data)

    def eof_received(self):
        raise NotImplementedError

    def connection_lost(self, error):
        super(ObProtocol, self).connection_lost(error)


