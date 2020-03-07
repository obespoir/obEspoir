# coding=utf-8
"""
author = jamon
"""

import ujson

from obespoir.share.ob_log import logger
from obespoir.base.common_define import NodeType
from obespoir.websocketserver.route import webSocketRouteHandle
from obespoir.rpcserver.push_lib import push_message


@webSocketRouteHandle
async def forward_0(command_id, data, session_id):
    """
    消息转发
    :param command_id: int
    :param data: json
    :param session_id: string
    :return: None
    """
    logger.debug("forward_0:{}".format([command_id, data, type(data), data, session_id]))
    if not isinstance(data, dict):
        try:
            data = ujson.loads(data)
            logger.debug("data type :{}".format(type(data)))
        except Exception:
            logger.warn("param data parse error {}".format(data))
            return {}
    data.update({"message_id": command_id})
    await push_message(NodeType.ROUTE, command_id, data, session_id=session_id, to=None)

