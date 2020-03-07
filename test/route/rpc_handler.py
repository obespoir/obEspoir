# coding=utf-8
"""
author = jamon
"""

from obespoir.base.common_define import NodeType
from obespoir.base.ob_handler import BaseHandler, RegisterEvent
from obespoir.rpcserver.push_lib import push_message
from obespoir.share.ob_log import logger


@RegisterEvent(1000)
class LoginHandler(BaseHandler):

    async def execute(self, *args, **kwargs):
        logger.info("login_handler:{}  {}".format(args, kwargs))
        user_name = self.params.get("name", "")
        passwd = self.params.get("passwd", "")
        if not user_name or not passwd:
            return {}
        # ...
        pass
        return {"code": 200, "data": {"user_id": 10, "desc": "恭喜，登录接口测试通过~"}}


@RegisterEvent(100130, need_return=False)
class OfflineHandler(BaseHandler):

    async def execute(self, *args, **kwargs):
        logger.info("offline: {}, {}".format(args, kwargs))
        pass
        return {"code": 200}


@RegisterEvent(10000, need_return=True)
class HeartBeatHandler(BaseHandler):

    async def execute(self, *args, **kwargs):
        logger.info("heartbeat: {}, {}".format(args, kwargs))
        pass
        return {"code": 200}

