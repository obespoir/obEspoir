# coding=utf-8

"""

"""

from Crypto.Cipher import AES
from share.singleton import Singleton
from share.ob_log import logger

import json

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[0:-ord(s[-1])]


class AesEncoder(object):
    __metaclass__ = Singleton

    NONE_TYPE = 0
    AES_TYPE = 1

    def __init__(self, password='helloworldiloveyou~1234567890123', encode_type=1):
        self.aes_obj = AES.new(password)
        self.encode_type = encode_type

    def encode(self, msg):
        if self.encode_type == self.NONE_TYPE:
            return msg
        elif self.encode_type == self.AES_TYPE:
            return self.encode_aes(msg)

    def encode_aes(self, msg):
        return self.aes_obj.encrypt(pad(msg))

    def decode_aes(self, msg):
        try:
            decode_msg = unpad(self.aes_obj.decrypt(msg))
        except Exception as e:
            logger.error("decode_aes error {}".format([msg]))
            return None

        msg_len = len(decode_msg)
        if msg_len == 0:
            return decode_msg

        try:
            json.loads(decode_msg)
        except ValueError:
            return None
        return decode_msg

    def decode(self, msg):
        if self.encode_type == self.NONE_TYPE:
            return msg
        elif self.encode_type == self.AES_TYPE:
            return self.decode_aes(msg)

    def byte_pad(self, text, byteAlignLen=16):
        count = len(text)
        mod_num = count % byteAlignLen
        if mod_num == 0:
            return text
        add_num = byteAlignLen - mod_num
        return text + chr(add_num) * add_num

    def byte_unpad(self,text, byteAlignLen=16):
        count = len(text)
        mod_num = count % byteAlignLen
        assert mod_num == 0
        lastChar = text[-1]
        lastLen = ord(lastChar)
        lastChunk = text[-lastLen:]
        if lastChunk == chr(lastLen) * lastLen:
            return text[:-lastLen]
        return text


if __name__ == "__main__":
    ret = AesEncoder().encode(json.dumps({"user_id": 1, "passwd":"123456"}))
    ret2 = AesEncoder().decode(ret)
    print(ret)
    print([ret2])