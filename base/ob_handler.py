# coding=utf-8
"""
author = jamon
"""


class BaseHandler(object):
    """
    基础命令处理类
    """
    def __init__(self, params, command_id, session_id):
        self.params = params
        self.command_id = command_id
        self.session_id = session_id

    async def execute(self, *args, **kwargs):
        raise NotImplementedError


class RegisterEvent(object):
    """
    事件管理器，将命令码与handler进行绑定
    """
    events = dict()

    def __init__(self, command_id, need_return=True):
        self.command_id = command_id
        self.need_return = need_return

    def __call__(self, handler):
        self.events[self.command_id] = {"handler": handler, "need_return": self.need_return}
        return handler