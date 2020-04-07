# coding=utf-8
"""
author = jamon
"""

# coding=utf-8

"""

"""

__all__ = [
    'getLogger',
    'DEBUG',
    'INFO',
    'WARN',
    'ERROR',
    'FATAL']

import os
import sys
import time
import logging
import logging.handlers
from datetime import datetime
from logging import getLogger, INFO, WARN, DEBUG, ERROR, FATAL, WARNING, CRITICAL, _levelToName


LOG_FILE_MAX_BYTES = 31457280
LOG_FILE_BACKUP_COUNT = 1000
LOG_LEVEL = logging.DEBUG

FORMAT = '[%(asctime)s | %(levelname)s %(filename)s:%(lineno)s(%(funcName)s)] -> %(message)s'
formatter = logging.Formatter(FORMAT)


level_dict = {
    "debug": DEBUG,
    "DEBUG": DEBUG,
    "info": INFO,
    "INFO": INFO,
    "warn": WARN,
    "WARN": WARN,
    "error": ERROR,
    "ERROR": ERROR
}


class ObLog(object):

    def __init__(self):
        self._normal = None
        self._error = None
        self.name = None
        self.log_dir = None
        self.last_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))   # 存放上一次打印日志的时间(字符串)
        self.log_type = "both"    # log_type: both|log|print

    def get_normal_log(self, date_format):
        file_name = '{0}/{1}_{2}.log'.format(self.log_dir, self.name, date_format)
        normal_handler = logging.handlers.RotatingFileHandler(file_name, maxBytes=LOG_FILE_MAX_BYTES,
                                                              backupCount=LOG_FILE_BACKUP_COUNT)
        normal_handler.setFormatter(formatter)
        normal_log = getLogger(self.name)
        normal_log.setLevel(LOG_LEVEL)
        normal_log.addHandler(normal_handler)
        return normal_log

    def get_error_log(self, date_format):
        file_name = '{0}/ERROR_{1}_{2}.log'.format(self.log_dir, self.name, date_format)
        error_handler = logging.handlers.RotatingFileHandler(file_name, maxBytes=LOG_FILE_MAX_BYTES,
                                                             backupCount=LOG_FILE_BACKUP_COUNT)
        error_handler.setFormatter(formatter)
        error_log = getLogger(self.name + '_error')
        error_log.setLevel(LOG_LEVEL)
        error_log.addHandler(error_handler)
        return error_log

    @property
    def normal_log(self):
        cur_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        if not self._normal or self.last_date != cur_date:
            self.last_date = cur_date
            if self.name in logging.Logger.manager.loggerDict.keys():
                logging.Logger.manager.loggerDict.pop(self.name)
            self._normal = self.get_normal_log(self.last_date)
        return self._normal

    @property
    def error_log(self):
        cur_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        if not self._error or self.last_date != cur_date:
            self.last_date = cur_date
            name = self.name + '_error'
            if name in logging.Logger.manager.loggerDict.keys():
                logging.Logger.manager.loggerDict.pop(name)
            self._error = self.get_error_log(self.last_date)
        return self._error

    def init(self, module_name, log_dir=None, level="debug", log_type="both"):
        self.set_module_name(module_name)
        self.log_type = log_type
        if "print" != self.log_type:
            if log_dir:
                self.set_log_dir(log_dir)
            self.set_level(level_dict.get(level))

    def set_module_name(self, name):
        self.name = name

    def set_log_dir(self, log_dir):
        """
        设置日志目录
        :param log_dir: string, absolute path, like "/data/logs/"
        :return:
        """
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.system("mkdir -p %s" % log_dir)

    def set_level(self, level):
        self.normal_log.setLevel(level)

    def _backup_print(self, level, msg, *args, **kwargs):
        back_file = sys._getframe().f_back.f_back
        rel_name = back_file.f_globals["__name__"].replace(".", "/") + ".py"
        cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        if args and args[0] and args[-1]:
            msg = "{0}/{1}".format(msg, str(args))
        if kwargs:
            msg = "{0}/{1}".format(msg, str(kwargs))
        print("[{0} {1} {2}:{3}({4})] -> {5} "
              .format(cur_time, _levelToName.get(level, "debug"), rel_name, back_file.f_code.co_name, back_file.f_lineno, msg))

    def debug(self, msg, *args, **kwargs):
        if self.log_type != "log":
            self._backup_print(DEBUG, msg, args, kwargs)

        if self.log_type != "print" and self.normal_log.isEnabledFor(DEBUG):
            self.normal_log._log(DEBUG, msg, args, **kwargs)

    def info(self, msg, *args, **kwargs):
        if self.log_type != "log":
            self._backup_print(INFO, msg, args, kwargs)

        if self.log_type != "print" and self.normal_log.isEnabledFor(INFO):
            self.normal_log._log(INFO, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.log_type != "log":
            self._backup_print(WARNING, msg, args, kwargs)

        if self.log_type != "print" and self.normal_log.isEnabledFor(WARNING):
            self.normal_log._log(WARNING, msg, args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        if self.log_type != "log":
            self._backup_print(WARN, msg, args, kwargs)

        if self.log_type != "print" and self.normal_log.isEnabledFor(WARN):
            self.normal_log._log(WARN, msg, args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.log_type != "log":
            self._backup_print(ERROR, msg, args, kwargs)

        if self.log_type != "print" and self.error_log.isEnabledFor(ERROR):
            self.normal_log._log(ERROR, msg, args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        if self.log_type != "log":
            self._backup_print(CRITICAL, msg, args, kwargs)

        if self.log_type != "print" and self.error_log.isEnabledFor(CRITICAL):
            self.normal_log._log(CRITICAL, msg, args, **kwargs)

    def fatal(self, msg, *args, **kwargs):
        if self.log_type != "log":
            self._backup_print(FATAL, msg, args, kwargs)

        if self.log_type != "print" and self.error_log.isEnabledFor(FATAL):
            self.normal_log._log(FATAL, msg, args, **kwargs)


logger = ObLog()
