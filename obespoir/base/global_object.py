# coding=utf-8
"""
author = jamon
"""

import hashlib

from obespoir.base.common_define import NodeType
from obespoir.share.singleton import Singleton


class GlobalObject(object, metaclass=Singleton):
    """
    全局对象
    """

    def __init__(self):
        self.name = None
        self.id = None
        self.type = -1

        self.http_server = None           # httpserver server

        self.rpc_server = None            # rpcserver server
        self.rpc_password = "helloworldiloveyou~1234567890123"
        self.rpc_encode_type = 0          # rpc加密类型
        self.rpc_route = {}               # 接收到rpc消息后的配置路由
        self.rpc_reconnect_time = 5

        self.ws_server = None             # websocketserver server
        self.ws_password = "helloworldiloveyou~1234567890123"
        self.ws_encode_type = 0           # websocket加密类型
        self.ws_timeout = 300
        self.ws_no_state_msg = {}        # 无状态的消息配置

        self.loop = None
        self.remote_ports = {}      # {type1: [{}, ...], type2: [{}, ...]}

    def init_from_config(self, config={}):
        """

        :param config: dict
        :return:
        """
        self.name = config["name"]
        self.type = NodeType.get_type(config["type"])

        self.rpc_password = config["rpc"]["token"]
        self.rpc_encode_type = config["rpc"]["encode"]
        # self.rpc_route = config["rpc"].get("route", {})
        self.rpc_reconnect_time = config["rpc"].get("reconnect_time", 5)
        if not self.format_rpc_route(config):
            raise Exception("route config error!")
        self.id = self.gen_id(config["host"], config["rpc"]["port"])

        if "websocket" in config.keys():
            self.ws_password = config["websocket"]["token"]
            self.ws_encode_type = config["websocket"]["encode"]
            self.ws_timeout = config["websocket"]["timeout"]
            self.ws_no_state_msg = config["websocket"].get("no_state", {})
            if not self.validate_no_state():
                raise Exception("ws_no_state_msg config error！")

    @staticmethod
    def gen_id(host, port):
        c_md5 = hashlib.md5()
        c_md5.update("{}_{}".format(host, port).encode("utf-8"))
        return c_md5.hexdigest()

    def update_remote_ports(self, remote_ports):
        """

        :param remote_ports: [{}, ...]
        :return:
        """
        for info in remote_ports:
            t = info.get("type")
            if t not in self.remote_ports.keys():
                self.remote_ports[t] = info
            else:
                self.remote_ports[t].append(info)

    def format_rpc_route(self, config):
        """
        验证路由配置是否正确, 格式化rpc配置信息
        :return: 0/1
        """
        rpc_route = config["rpc"].get("route", {})
        for type_name, route in rpc_route.get("range", {}).items():
            if not isinstance(route, list):
                return 0

            for r in route:
                if not isinstance(r, list):
                    return 0
                if 2 != len(r) or r[0]>r[1] or not isinstance(r[0], int) or not isinstance(r[1], int):
                    return 0

        for type_name, route in self.rpc_route.get("special", {}).items():
            for s in route:
                if not isinstance(s, int):
                    return 0

        self.rpc_route = {"range": {}, "special": {}}
        for type_name, route in rpc_route.get("range", {}).items():
            self.rpc_route["range"][NodeType.get_type(type_name)] = route
        for type_name, route in rpc_route.get("special", {}).items():
            self.rpc_route["special"][NodeType.get_type(type_name)] = route

        return 1

    def validate_no_state(self):
        """
        验证路由配置是否正确
        :return: 0/1
        """
        for info in self.ws_no_state_msg.get("range", []):
            if not isinstance(info, list):
                return 0

            if 2 != len(info) or info[0]>info[1] or not isinstance(info[0], int) or not isinstance(info[1], int):
                return 0

        for info in self.ws_no_state_msg.get("special", []):
            for s in info:
                if not isinstance(s, int):
                    return 0

        return 1

