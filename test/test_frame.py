# coding=utf-8
"""
author = jamon
"""

import asyncio
import requests
import struct
import ujson
import websockets

from share.encodeutil import AesEncoder


class RpcProtocol(object):
    """消息协议，包含消息处理"""

    def __init__(self):
        self.handfrt = "iii"  # (int, int, int)  -> (message_length, command_id, version)
        self.head_len = struct.calcsize(self.handfrt)
        self.identifier = 0

        self.encode_ins = AesEncoder()
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
        :return:
        """
        print(type(data))
        data = self.encode_ins.encode(data)
        # data = "%s" % data
        length = data.__len__() + self.head_len
        head = struct.pack(self.handfrt, length, command_id, self.version)
        print("type=", type(head), type(data), [head], head[0])
        print(struct.unpack(self.handfrt, head))
        return (head + data).decode("utf8")


def test_http_web_proxy():
    url = "http://127.0.0.1:20001/"
    ret = requests.post(url, data=ujson.dumps({"token": "19778225bc81894d8a6465c93542c0",
                                               "phone": [1, 2], "content": "test"
                                               }))
    print("test_http_web_proxy:", ret.status_code, ret.text)


async def test_websocket_proxy():
    async with websockets.connect("ws://127.0.0.1:20000") as websocket:
        name = "jamon"
        print("send server: ", name)
        data = RpcProtocol().pack(ujson.dumps({"name": name}), 0)
        print("data=", data)
        await websocket.send(data)
        greeting = await websocket.recv()
        print("receive from server: ", greeting)
        # ret = await websocket.close(reason="user exit")
        ret = await asyncio.sleep(10)
        print("t::::::", ret)




if __name__ == "__main__":
    # test_http_web_proxy()
    asyncio.get_event_loop().run_until_complete(test_websocket_proxy())