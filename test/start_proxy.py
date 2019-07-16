# coding=utf-8
"""
author = jamon
"""


if __name__ == "__main__":
    import sys
    sys.path.append("../")    # 添加项目的根目录到系统路径中

import logging

from share.parse_json import ParseJson
from server.server import Server
from share.ob_log import logger


if __name__ == "__main__":
    main_server = Server()
    serv_config = ParseJson.loads("../proxy_config.json")

    logger.init(module_name=serv_config.get("service_name"),log_dir=serv_config.get("log_dir", "../logs/")
                , level=serv_config.get("log_level", logging.DEBUG))

    main_server.config(serv_config)
    main_server.run()

