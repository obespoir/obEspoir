# coding=utf-8
"""
author = jamon
"""

import asyncio
import struct
import threading
from websockets.server import WebSocketServerProtocol

from obespoir.base.common_define import CLIENT_OFFLINE
from obespoir.base.global_object import GlobalObject
from obespoir.base.ob_protocol import DataException
from obespoir.rpcserver.session_cache import SessionCache
from obespoir.share.encodeutil import AesEncoder
from obespoir.websocketserver.route import websocket_route
from obespoir.websocketserver.manager import WebsocketConnectionManager


class WebSocketProtocol(WebSocketServerProtocol):
    """消息协议，包含消息处理"""

    cur_seq = 0
    lock = threading.RLock()

    @classmethod
    def gen_new_seq(cls):
        cls.lock.acquire()
        try:
            cls.cur_seq += 1
            return cls.cur_seq
        finally:
            cls.lock.release()

    def __init__(self, ws_handler, ws_server, *,
                 origins=None, extensions=None, subprotocols=None,
                 extra_headers=None, **kwds):
        self.handfrt = "iii"  # (int, int, int)  -> (message_length, command_id, version)
        self.head_len = struct.calcsize(self.handfrt)
        self.seq = None
        self.session_id = ""

        self.encode_ins = AesEncoder(GlobalObject().rpc_password, encode_type=GlobalObject().rpc_encode_type)
        self.version = 0

        self._buffer = b""    # 数据缓冲buffer
        self._head = None     # 消息头, list,   [message_length, command_id, version]
        self.transport = None
        super().__init__(ws_handler, ws_server, **kwds)

    def connection_open(self):
        super().connection_open()
        self.seq = WebSocketProtocol.gen_new_seq()
        self.session_id = "{}_{}".format(GlobalObject().id, self.seq)
        WebsocketConnectionManager().store_connection(self.seq, self)

    def connection_made(self, transport):
        super().connection_made(transport)
        self.transport = transport

    def connection_lost(self, exc):
        super().connection_lost(exc)
        WebsocketConnectionManager().remove_connection(self)
        SessionCache().del_cache(self.session_id)
        # client连接断开
        asyncio.ensure_future(websocket_route.call_target(CLIENT_OFFLINE, {}, session_id=self.session_id)
                              , loop=GlobalObject().loop)
        # GlobalObject().loop.run_until_complete(
        #     websocket_route.call_target(CLIENT_OFFLINE, {}, session_id=self.session_id))

    async def send_message(self, result, command_id):
        data = self.pack(result, command_id)
        print("ddddddd:", data, type(self), self)
        await self.send(data)

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
        print("message_handle:", data, websocket, type(websocket))
        result = await websocket_route.call_target(command_id, data, session_id=self.session_id)
        if result:
            websocket.send(self.pack(result, command_id).decode("utf8"))
