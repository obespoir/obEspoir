# coding=utf-8
"""
author = jamon
"""

from share.singleton import Singleton


class GlobalObject:
    """
    全局对象
    """
    __metaclass__ = Singleton

    def __init__(self):
        self.http_server = None           # http server
        self.rpc_server = None            # rpc server
        self.ws_server = None             # websocket server

