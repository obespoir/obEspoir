# coding=utf-8
"""
author = jamon
"""


import asyncio
import websockets

from aiohttp import web
from server.ob_protocol import ObProtocol
from server.rpc_push import RpcPushProtocol
from server.rpc_connection_manager import RpcConnectionManager
from server.global_object import GlobalObject
from share.ob_log import logger


try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class Server(object):
    """
    启动server主类
    """

    def __init__(self):
        self.host = None
        self.web_handler = {}
        self.socket_handler = None
        self.rpc_handler = None
        self.loop = asyncio.get_event_loop()

    def register_web_route(self, url, handler):
        """

        :param url: 相对地址， like "/login"
        :param handler:
        :return:
        """
        self.web_handler[url] = handler

    def register_socket_route(self, handler):
        """

        :param handler:
        :return:
        """
        self.socket_handler = handler

    def register_rpc_route(self, handler):
        """

        :param handler:
        :return:
        """
        self.rpc_handler = handler

    async def start_web(self, web_port):
        "http协议 web"
        app = web.Application()
        self.web_handler["/update_config"] = self.update_config_remote
        for k, v in self.web_handler.items():
            app.router.add_route("*", k, v)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, web_port)
        logger.info('server started at http://{0}:{1}...'.format(self.host, web_port))
        await site.start()

    def config(self, config):
        """

        :param config:
        :return:
        """
        host = config.get("host")
        self.host = host
        ws_port = config["websocket"].get("ws_port", 0)      # web_socket port
        web_port = config["http"].get("web_port", 0)    # web http port
        rpc_port = config["rpc"].get("rpc_port", 0)    # rpc port
        remote_ports = config.get("remote_ports", [])   # remote_ports list
        print([self.host, ws_port, web_port, rpc_port])

        if ws_port and self.socket_handler:
            GlobalObject().ws_server = self.loop.run_until_complete(
                websockets.serve(self.socket_handler, self.host, ws_port))

        if web_port and self.web_handler:
            GlobalObject().http_server = self.loop.run_until_complete(self.start_web(web_port))

        if rpc_port:
            GlobalObject().rpc_server = self.loop.run_until_complete(
                self.loop.create_server(ObProtocol, self.host, rpc_port))

        if remote_ports:
            for rp in remote_ports:
                host = rp.get("host", "")
                port = rp.get("port", 0)
                s_type = rp.get('type', 1)
                if host and port:
                    remote_serv = self.loop.create_connection(RpcPushProtocol, host=host, port=port)
                    RpcConnectionManager().add_type_node(s_type, host, port)
                    try:
                        self.loop.run_until_complete(remote_serv)
                    except ConnectionRefusedError as e:
                        logger.info("connect to {}:{} failed!".format(host, port))

    async def update_config_remote(self, server_type, addr_info={}):
        """
        更新远程rpc连接
        :param server_type: int, 待更新的服务节点类型
        :param addr_info: dict, {host: port1, host2: port2, ...}
        :return:
        """
        remote_names = ["{}_{}".format(k, v) for k, v in addr_info.items()]
        for r in RpcConnectionManager().conns.keys():
            if r not in remote_names:
                if RpcConnectionManager().conns[r]["status"] == 1:
                    RpcConnectionManager().conns[r]["transport"].close()
                RpcConnectionManager().conns.pop(r)
        for k, v in addr_info.items():
            name = "{}_{}".format(k, v)
            if name not in RpcConnectionManager().conn.keys() or RpcConnectionManager().conns[name].status != 1:
                RpcConnectionManager().add_type_node(server_type, k, v)
                remote_serv = await self.loop.create_connection(RpcPushProtocol, host=k, port=v)
                try:
                    self.loop.run_until_complete(remote_serv)
                except ConnectionRefusedError as e:
                    logger.error("connect to {}:{} failed!")

    async def send_message(self, remote_name, message):
        if remote_name not in RpcConnectionManager().conns.keys():
            return
        await RpcConnectionManager().send_message(remote_name, message)

    def run(self):
        try:
            self.loop.run_forever()
        finally:
            if GlobalObject().http_server:
                GlobalObject().http_server.close()
                self.loop.run_until_complete(GlobalObject().http_server.wait_closed())
            if GlobalObject().rpc_server:
                GlobalObject().rpc_server.close()
                self.loop.run_until_complete(GlobalObject().rpc_server.wait_closed())
            if GlobalObject().ws_server:
                GlobalObject().ws_server.close()
                self.loop.run_until_complete(GlobalObject().ws_server.wait_closed())
            self.loop.close()





