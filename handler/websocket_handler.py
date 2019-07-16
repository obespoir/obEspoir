# coding=utf-8
"""
author = jamon
"""




async def websocket_handler(websocket, path):
    while True:
        recv_text = await websocket.recv()
        response_text = f"your submit context: {recv_text}"
        await websocket.send(response_text)

