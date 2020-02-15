# coding=utf-8
"""
author = jamon
"""


from share.singleton import Singleton


class WebsocketConnectionManager(object, metaclass=Singleton):

    def __init__(self):
        self.conns = {}       # 会话序号（int）和websocket对象对应关系

    def store_connection(self, seq, websocket):
        if seq not in self.conns.keys():
            self.conns[seq] = websocket
        return 1

    def remove_connection(self, websocket):
        if websocket in self.conns.values():
            self.conns.pop(websocket.seq)
        return 1

    def get_websocket(self, seq):
        if seq not in self.conns.keys():
            return
        return self.conns[seq]

