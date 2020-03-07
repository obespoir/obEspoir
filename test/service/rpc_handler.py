# coding=utf-8
"""
author = jamon
"""

from obespoir.base.common_define import NodeType
from obespoir.base.ob_handler import BaseHandler, RegisterEvent
from obespoir.rpcserver.push_lib import push_message
from obespoir.share.ob_log import logger


@RegisterEvent(20000)
class EnterRankHandler(BaseHandler):

    async def execute(self, *args, **kwargs):
        logger.info("enter_rank_room_handler:{}  {}".format(args, kwargs))
        user_id = self.params.get("user_id", -1)
        if -1 == user_id:
            return {}
        # ...
        pass
        return {"code": 200, "data": {"desc": "恭喜，进入排位场房间接口测试通过~"}}


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