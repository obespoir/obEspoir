# coding=utf-8
"""
author = jamon
"""

import threading

from share.ob_log import logger


class ObService(object):
    """消息分发"""

    def __init__(self):
        self._lock = threading.RLock()
        self._targets = {}  # Keeps track of targets internally

    def __iter__(self):
        return self._targets.values()

    def map_target(self, target):
        """Add a target to the service."""
        self._lock.acquire()
        try:
            key = target.__name__
            if key in self._targets.keys():
                exist_target = self._targets.get(key)
                raise "target [%d] Already exists,\
                Conflict between the %s and %s" % (key, exist_target.__name__, target.__name__)
            self._targets[key] = target
        finally:
            self._lock.release()

    def unmap_target(self, target):
        """Remove a target from the service."""
        self._lock.acquire()
        try:
            key = target.__name__
            if key in self._targets.keys():
                del self._targets[key]
        finally:
            self._lock.release()

    def unmap_target_by_key(self, targetKey):
        """Remove a target from the service."""
        self._lock.acquire()
        try:
            del self._targets[targetKey]
        finally:
            self._lock.release()

    def get_target(self, targetKey):
        """Get a target from the service by name."""
        self._lock.acquire()
        try:
            target = self._targets.get(targetKey, None)
        finally:
            self._lock.release()
        return target

    async def call_target(self, targetKey, *args, **kw):
        '''call Target
        @param conn: client connection
        @param targetKey: target ID
        @param data: client data
        '''
        target = self.get_target(targetKey)

        self._lock.acquire()
        try:
            if not target:
                logger.err('the command ' + str(targetKey) + ' not Found on service')
                return None

            result = await target(*args, **kw)

            return result
        finally:
            self._lock.release()


rpc_service = ObService()
websocket_service = ObService()


def RpcServiceHandle(target):
    rpc_service.map_target(target)


def WebSocketServiceHandle(target):
    websocket_service.map_target(target)
