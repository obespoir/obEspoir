# coding=utf-8
"""
author = jamon
"""

from share.ob_log import logger
from share.singleton import Singleton


class RpcConnectionManager(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.conns = {}     # {conn_name: {status: int(0:未连接，1：连接中，2：连接断开), transport: transport}}
        self.type_dict = {}  # 存放节点类型信息 {int: [conn_name1, conn_name2, ...]}

    def __gen_name(self, host, port):
        return "{}_{}".format(host, port)

    def get_transport(self, host, port):
        name = self.__gen_name(host, port)
        if name not in self.conns.keys() or 1 != self.conns[name]["status"]:
            return None
        return self.conns[name]["transport"]

    def store_connection(self, host, port, transport):
        self.conns[self.__gen_name(host, port)] = {"status": 1, "transport": transport}

    def lost_connection(self, host, port):
        name = self.__gen_name(host, port)
        if name not in self.conns.keys():
            logger.warn("can not find connection {}".format(name))
            return 0
        self.conns[name]["transport"].close()
        self.conns[name]["status"] = 2

    def remove_connection(self, conn_name):
        if conn_name not in self.conns.keys():
            return 0
        self.conns[conn_name]["transport"].close()
        self.conns.pop(conn_name)
        return 1

    def add_type_node(self, node_type, host, port):
        name = self.__gen_name(host, port)
        if node_type not in self.type_dict.keys():
            self.type_dict[node_type] = [name]
        else:
            if name not in self.type_dict[node_type]:
                self.type_dict[node_type].append(name)

    def del_type_node(self, node_type, host, port):
        name = self.__gen_name(host, port)
        if node_type in self.type_dict.keys():
            if name in self.type_dict[node_type]:
                self.type_dict[node_type].remove(name)

    def send_message(self, node_name, message):
        """
        向指定连接发送消息
        :param node_name:
        :param message:
        :return:
        """
        if node_name not in self.conns.keys() or 1 != self.conns[node_name]["status"]:
            logger.warn("can not find connection {}".format(node_name))
            return

        self.conns[node_name]["transport"].write(message)
        logger.debug("rpc send {0}".format(message))
        return 1
