# coding=utf-8
"""
author = jamon
"""

from base.ob_route import ObRoute


rpc_route = ObRoute()


def rpcRouteHandle(target):
    rpc_route.map_target(target)





