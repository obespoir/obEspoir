# coding=utf-8
"""
author = jamon
"""


if __name__ == "__main__":
    import sys
    sys.path.append("../")    # 添加项目的根目录到系统路径中

import logging

from handler.websocket_handler import WebsocketHandler
from share.parse_json import ParseJson
from server.server import Server
from share.ob_log import logger


if __name__ == "__main__":
    main_server = Server()
    main_server.register_socket_route(WebsocketHandler().websocket_handler)
    serv_config = ParseJson.loads("../proxy_config.json")

    logger.init(module_name=serv_config.get("service_name"), log_dir=serv_config.get("log_dir", "../logs/")
                , level=serv_config.get("log_level", logging.DEBUG))

    main_server.start(serv_config)
    # main_server.config(serv_config)
    # main_server.run()

