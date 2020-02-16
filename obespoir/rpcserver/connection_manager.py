# coding=utf-8
"""
author = jamon
"""

import asyncio
import random
import ujson

from obespoir.base.common_define import ConnectionStatus
from obespoir.base.global_object import GlobalObject
from obespoir.share.ob_log import logger
from obespoir.share.singleton import Singleton


class RpcConnectionManager(object, metaclass=Singleton):

    def __init__(self):
        self.conns = {}     # {conn_name: {status: int(0:未连接，1：连接中，2：连接断开), conn: connect object}}
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
        返回一个可用的连接名
        :param node_type:
        :return: node name
        """
        cur_nodes = self.type_dict.get(node_type, [])
        available_nodes = []
        print("get_available_connection: type_dict({}), conns({}), cur_nodes({})"
              .format(self.type_dict, self.conns, cur_nodes))
        for name in cur_nodes:
            if ConnectionStatus.ESTABLISHED == self.conns[name]["status"]:
                available_nodes.append(name)
        return random.choice(available_nodes)

    def store_connection(self, host, port, connect, status=ConnectionStatus.LOSE):
        print("store_connection:", host, port, connect)
        self.conns[RpcConnectionManager.gen_node_name(host, port)] = {
            "status": status, "conn": connect, "host": host, "port": port}

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

    async def send_message(self, node_name, command_id, data, session_id=None, to=None):
        """
        向指定连接发送消息
        :param node_name: string
        :param command_id: int
        :param message:
        :return:
        """
        if node_name not in self.conns.keys():
            print("sssssssss:", self.conns)
            logger.warn("can not find connection {}".format(node_name))
            return

        if ConnectionStatus.ESTABLISHED != self.conns[node_name]["status"]:
            # 连接断开状态
            logger.warn("connection is unavailable {}".format(node_name))
            for reconnect_times in range(3):
                await asyncio.sleep(5)
                if ConnectionStatus.ESTABLISHED == self.conns[node_name]["status"]:
                    break
                if 2 == reconnect_times:
                    logger.error("exceed max reconnect times {}".format(node_name))
                    return

        if not isinstance(data, str):
            data = ujson.dumps(data)
        print(data, data.encode("utf8"), type(data))
        await self.conns[node_name]["conn"].send_message(command_id, data, session_id=session_id , to=to)
        logger.debug("rpcserver send {0}".format(data))
        return 1
