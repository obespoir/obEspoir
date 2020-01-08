# coding=utf-8
"""
author = jamon
"""

import random
import ujson

from base.common_define import ConnectionStatus
from base.global_object import GlobalObject
from share.ob_log import logger
from share.singleton import Singleton


class RpcConnectionManager(object, metaclass=Singleton):

    def __init__(self):
        self.conns = {}     # {conn_name: {status: int(0:未连接，1：连接中，2：连接断开), transport: transport}}
        self.type_dict = {}  # 存放节点类型信息 {int: [conn_name1, conn_name2, ...]}
    
    @staticmethod
    def gen_node_name(host, port):
        return GlobalObject.gen_id(host, port)

    def get_connection(self, host, port):
        name = RpcConnectionManager.gen_node_name(host, port)
        if name not in self.conns.keys() or ConnectionStatus.ESTABLISHED != self.conns[name]["status"]:
            return None
        return self.conns[name]["conn"]

    def get_available_connection(self, node_type):
        """
        返回一个可用的连接
        :param node_type:
        :return:
        """
        cur_nodes = self.type_dict.get(node_type, [])
        available_nodes = []
        for name in cur_nodes:
            if ConnectionStatus.ESTABLISHED == self.conns[name]["status"]:
                available_nodes.append(self.conns[name]["conn"])
        return random.choice(available_nodes)

    def store_connection(self, host, port, connect):
        self.conns[RpcConnectionManager.gen_node_name(host, port)] = {
            "status": ConnectionStatus.ESTABLISHED, "conn": connect}

    def lost_connection(self, host, port):
        name = RpcConnectionManager.gen_node_name(host, port)
        if name not in self.conns.keys():
            logger.warn("can not find connection {}".format(name))
            return 0
        self.conns[name]["conn"].transport.close()
        self.conns[name]["status"] = ConnectionStatus.LOSE

    def remove_connection(self, conn_name):
        if conn_name not in self.conns.keys():
            return 0
        self.conns[conn_name]["conn"].transport.close()
        self.conns.pop(conn_name)
        return 1

    def add_type_node(self, node_type, host, port):
        name = RpcConnectionManager.gen_node_name(host, port)
        if node_type not in self.type_dict.keys():
            self.type_dict[node_type] = [name]
        else:
            if name not in self.type_dict[node_type]:
                self.type_dict[node_type].append(name)
        # print(self.type_dict, id(self), id(self.type_dict))

    def del_type_node(self, node_type, host, port):
        name = RpcConnectionManager.gen_node_name(host, port)
        if node_type in self.type_dict.keys():
            if name in self.type_dict[node_type]:
                self.type_dict[node_type].remove(name)

    async def send_message(self, node_name, command_id, data, src=None, to=None):
        """
        向指定连接发送消息
        :param node_name: string
        :param command_id: int
        :param message:
        :return:
        """
        if node_name not in self.conns.keys() or ConnectionStatus.ESTABLISHED != self.conns[node_name]["status"]:
            print("sssssssss:", self.conns)
            logger.warn("can not find connection {}".format(node_name))
            return

        if not isinstance(data, str):
            data = ujson.dumps(data)
        print(data, data.encode("utf8"), type(data))
        await self.conns[node_name]["conn"].send_message(command_id, data, src=src, to=to)
        logger.debug("rpc send {0}".format(data))
        return 1
