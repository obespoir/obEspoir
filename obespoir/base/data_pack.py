# coding=utf-8
"""
author = jamon
"""

import struct

from obespoir.share.encodeutil import AesEncoder


class DataPack(object):

    def __init__(self, password, is_encode=0):
        self.handfrt = "iii"        # (int, int, int)  -> (message_length, command_id, version)
        self.identifier = 0
        self.aes_ins = AesEncoder()
        self.version = 0

    def get_head_len(self):
        return struct.calcsize(self.handfrt)

    def unpack(self, pack_data):
        head_len = self.get_head_len()
        if head_len > len(pack_data):
            return None

        data_head = pack_data[0:head_len]
        list_head = struct.unpack(self.handfrt, data_head)
        data = pack_data[head_len:]
        result = self.aes_ins.decode_aes(data)
        if not result:
            result = {}

        return {'result': True, 'command': list_head[1], 'data': result}

    def pack(self, data, command_id):
        """
        打包消息， 用於傳輸
        :param data:  傳輸數據
        :param command_id:  消息ID
        :return:
        """
        data = self.aes_ins.encode(data)
        data = "%s" % data
        length = data.__len__() + self.get_head_len()
        head = struct.pack(self.handfrt, length, command_id, self.version)
        return str(head + data)
