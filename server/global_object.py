# coding=utf-8
"""
author = jamon
"""

from share.singleton import Singleton


class GlobalObject(object, metaclass=Singleton):
    """
    全局对象
    """

    def __init__(self):
        self.http_server = None           # http server

        self.rpc_server = None            # rpc server
        self.rpc_password = "helloworldiloveyou~1234567890123"
        self.rpc_encode_type = 0          # rpc加密类型

        self.ws_server = None             # websocket server
        self.ws_password = "helloworldiloveyou~1234567890123"
        self.ws_encode_type = 0           # websocket加密类型
        self.ws_timeout = 300
        self.ws_route = {}

    def init_from_config(self, config={}):
        """

        :param config: dict
        :return:
        """
        self.rpc_password = config["rpc"]["token"]
        self.rpc_encode_type = config["rpc"]["encode"]

        self.ws_password = config["websocket"]["token"]
        self.ws_encode_type = config["websocket"]["encode"]
        self.ws_timeout = config["websocket"]["timeout"]
        self.ws_route = config["websocket"]["route"]
        if not self.validate_route():
            raise Exception("route config error!")

    def validate_route(self):
        """
        验证路由配置是否正确
        :return: 0/1
        """
        for type_name, route in self.ws_route["range"].items():
            if not isinstance(route, list):
                return 0

            for r in route:
                if not isinstance(r, list):
                    return 0
                if 2 != len(r) or r[0]>r[1] or not isinstance(r[0], int) or not isinstance(r[1], int):
                    return 0

        for type_name, route in self.ws_route["special"].items():
            for s in route:
                if not isinstance(s, int):
                    return 0

        return 1

