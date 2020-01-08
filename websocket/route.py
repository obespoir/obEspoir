# coding=utf-8
"""
author = jamon
"""

from base.ob_route import ObRoute


class WebSocketRoute(ObRoute):

    def get_target(self, targetKey):
        """Get a target from the service by name."""
        self._lock.acquire()
        try:
            target = self._targets.get(targetKey, None)
            if not target:
                target = self._targets.get(0, None)
        finally:
            self._lock.release()
        return target


websocket_route = WebSocketRoute()


def webSocketRouteHandle(target):
    websocket_route.map_target(target)