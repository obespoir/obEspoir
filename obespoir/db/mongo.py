# coding=utf-8
"""
author = jamon
"""

from pymongo import MongoClient

from obespoir.share.ob_log import logger


class AvailServerConfig(object):
    """
    rpc可用的节点配置
    数据设计结构:
    remote_ports: [
        {
            "host": "127.0.0.1",
            "port":  21002,
            "token": "helloworldiloveyou~1234567890123",
            "encode": 0,
            "type": "route"                      // 节点类型(字符串标识)
        }
    ]
    """
    _instance = None
    _database_name = "obespoir"
    _table_name = "config"

    @classmethod
    def get_instance(cls, uri):
        if not cls._instance:
            cls._instance = AvailServerConfig(uri)
        return cls._instance

    def __init__(self, uri):
        self.conn = MongoClient(uri)[AvailServerConfig._database_name][AvailServerConfig._table_name]

    def insert(self, param_name, config):
        """

        :param param_name: str, 配置参数名
        :param config: json(dict|list), 待插入的配置信息
        :return:
        """
        self.conn.insert({"name": param_name, "info": config})
        logger.info("insert to mongo: {}, {}".format(param_name, config))
        return

    def get_remote_ports(self):
        """
        获取remote_ports配置信息
        :return: list
        """
        ret = self.conn.find({"name": "remote_ports"}, projection={"_id": False, "name": False})
        result = []
        for r in ret:
            result.append(r.get("info", {}))
        return result


if __name__ == "__main__":
    AvailServerConfig.get_instance().insert("nawHtSjCK8MC77fVb1n3h8xPI08jji1A", "201809/20/1.txt", 1538048261,
                                            1538048261, "tencent")

