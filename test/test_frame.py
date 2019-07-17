# coding=utf-8
"""
author = jamon
"""

import asyncio
import requests
import ujson
import websockets


def test_http_web_proxy():
    url = "http://127.0.0.1:20001/"
    ret = requests.post(url, data=ujson.dumps({"token": "19778225bc81894d8a6465c93542c0",
                                               "phone": [1,2], "content": "test"
                                               }))
    print("test_http_web_proxy:", ret.status_code, ret.text)


async def test_websocket_proxy():
    async with websockets.connect("ws://127.0.0.1:20000") as websocket:
        name = input("what's your name? ")
        await websocket.send(name)
        print("send server: ", name)
        greeting = await websocket.recv()
        print("receive from server: ", greeting)
        # ret = await websocket.close(reason="user exit")
        ret = await asyncio.sleep(10)
        print("t::::::", ret)


# def hello_client():
#     a = websockets.connect("ws://localhost:20000")
#     with websockets.connect("ws://localhost:20000") as websocket:
#         name = input("what's your name? ")
#         websocket.send(name)
#         print("send server: ", name)
#         greeting = websocket.recv()
#         print("receive from server: ", greeting)
#
# hello_client()
# asyncio.get_event_loop().run_until_complete(hello_client())

if __name__ == "__main__":
    # test_http_web_proxy()
    asyncio.get_event_loop().run_until_complete(test_websocket_proxy())