# coding=utf-8
"""
author = jamon
"""


import asyncio
from contextlib import suppress
import websockets

from aiohttp import web

from obespoir.base.common_define import NodeType, ConnectionStatus
from obespoir.db.mongo import AvailServerConfig
from obespoir.rpcserver.protocol import RpcProtocol
from obespoir.rpcserver.push_protocol import RpcPushProtocol
from obespoir.rpcserver.connection_manager import RpcConnectionManager
from obespoir.websocketserver.protocol import WebSocketProtocol
from obespoir.base.global_object import GlobalObject
from obespoir.share.ob_log import logger
from obespoir.share.singleton import Singleton


try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class Server(object, metaclass=Singleton):
    """
    启动server主类
    """

    def __init__(self):
        self.host = None
        self.web_handler = {}
        self.socket_handler = None
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

    async def start_web(self, web_port):
        "http协议 web"
        app = web.Application()
        for k, v in self.web_handler.items():
            app.router.add_route("*", k, v)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, web_port)
        logger.info('server started at httpserver://{0}:{1}...'.format(self.host, web_port))
        await site.start()

    def config(self, config):
        """

        :param config:
        :return:
        """
        host = config.get("host")
        self.host = host
        ws_port = config.get("websocket", {}).get("port", 0)      # web_socket port
        web_port = config.get("http", {}).get("port", 0)    # web httpserver port
        rpc_port = config.get("rpc", {}).get("port", 0)    # rpcserver port
        remote_ports = config.get("remote_ports", [])   # remote_ports list
        if "mongo" == config.get("available_way", "local") and config.get("mongo_uri", ""):
            # 如果高可用使用的是MongoDB存储配置方式
            remote_ports = AvailServerConfig.get_instance(uri=config.get("mongo_uri"))
        GlobalObject().update_remote_ports(remote_ports)
        api_path = config.get("api_path", "")
        if api_path:
            __import__(api_path)

        GlobalObject().loop = self.loop

        GlobalObject().init_from_config(config)

        if ws_port and self.socket_handler:    # websocketserver port start
            GlobalObject().ws_server = self.loop.run_until_complete(
                websockets.serve(self.socket_handler, self.host, ws_port, create_protocol=WebSocketProtocol))

        if web_port and self.web_handler:      # web httpserver port  start
            GlobalObject().http_server = self.loop.run_until_complete(self.start_web(web_port))

        if rpc_port:
            GlobalObject().rpc_server = self.loop.run_until_complete(
                self.loop.create_server(RpcProtocol, self.host, rpc_port))

        if remote_ports:
            for rp in remote_ports:
                host = rp.get("host", "")
                port = rp.get("port", 0)
                s_type = NodeType.get_type(rp.get('type'))
                if host and port:
                    RpcConnectionManager().add_type_node(s_type, host, port)
                    RpcConnectionManager().store_connection(host, port, None)
                    if not RpcConnectionManager().get_connection(host, port):
                        remote_serv = self.loop.create_connection(RpcPushProtocol, host=host, port=port)
                        try:
                            self.loop.run_until_complete(remote_serv)
                        except ConnectionRefusedError:
                            print("HERE", RpcConnectionManager().conns)
                            logger.info("connecting to {}:{} failed!".format(host, port))

    async def update_remote_rpc_config(self):
        """
        更新远程rpc连接
        :param server_type: int, 待更新的服务节点类型
        :param addr_info: dict, {host: port1, host2: port2, ...}
        :return:
        """
        for server_type, addr_info in GlobalObject().remote_ports.items():
            remote_names = [RpcConnectionManager.gen_node_name(k, v) for k, v in addr_info.items()]
            for r in RpcConnectionManager().conns.keys():
                if r not in remote_names:
                    if RpcConnectionManager().conns[r]["status"] == ConnectionStatus.ESTABLISHED:
                        RpcConnectionManager().conns[r]["conn"].transport.close()
                    RpcConnectionManager().conns.pop(r)
            for k, v in addr_info.items():
                name = RpcConnectionManager.gen_node_name(k, v)
                if name not in RpcConnectionManager().conns.keys() \
                        or RpcConnectionManager().conns[name]["status"] != ConnectionStatus.ESTABLISHED:
                    RpcConnectionManager().add_type_node(server_type, k, v)
                    RpcConnectionManager().store_connection(k, v, None)
                    try:
                        await self.loop.create_connection(RpcPushProtocol, host=k, port=v)
                        logger.info("success connect to {}:{}".format(k, v))
                    except ConnectionRefusedError as e:
                        logger.error("try connect to {}:{} failed!")

    async def send_message(self, remote_name, message):
        if remote_name not in RpcConnectionManager().conns.keys():
            return
        await RpcConnectionManager().send_message(remote_name, message)

    def start(self, config):
        self.config(config)
        # self.loop.run_until_complete(self.schedule())
        asyncio.run_coroutine_threadsafe(self.schedule(), self.loop)
        self.run()

    async def schedule(self):
        # 定时rpc断线重连
        while True:
            await asyncio.sleep(3)
            # logger.info("start new schedule task~")
            # print("schedule:", RpcConnectionManager().type_dict, RpcConnectionManager().conns)
            for node_type, name_lst in RpcConnectionManager().type_dict.items():
                for name in name_lst:
                    if name not in RpcConnectionManager().conns.keys()\
                            or ConnectionStatus.ESTABLISHED != RpcConnectionManager().conns[name]["status"]:
                        host = RpcConnectionManager().conns[name]["host"]
                        port = RpcConnectionManager().conns[name]["port"]
                        try:
                            print("try to reconnect:",name,  host, port)
                            await self.loop.create_connection(RpcPushProtocol, host=host, port=port)
                            logger.info("success connect to {}:{}".format(host, port))
                        except ConnectionRefusedError as e:
                            logger.error("schedule try connect to {}:{} failed!")

    def run(self):
        try:
            self.loop.run_forever()
        finally:
            pending = asyncio.Task.all_tasks()
            for task in pending:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    self.loop.run_until_complete(task)
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




