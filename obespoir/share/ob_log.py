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
import time
import logging
import logging.handlers
from logging import getLogger, INFO, WARN, DEBUG, ERROR, FATAL, WARNING, CRITICAL


LOG_FILE_MAX_BYTES = 31457280
LOG_FILE_BACKUP_COUNT = 1000
LOG_LEVEL = logging.DEBUG

FORMAT = '[%(asctime)s]-%(levelname)-8s<%(name)s> {%(filename)s:%(lineno)s} -> %(message)s'
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
            self._normal = self.get_normal_log(self.last_date)
        return self._normal

    @property
    def error_log(self):
        cur_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        if not self._error or self.last_date != cur_date:
            self.last_date = cur_date
            self._error = self.get_error_log(self.last_date)
        return self._error

    def init(self, module_name, log_dir, level):
        self.set_module_name(module_name)
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

    def _backup_print(self, msg, *args, **kwargs):
        if args:
            msg = "{0}/{1}".format(msg, str(args))
        if kwargs:
            msg = "{0}/{1}".format(msg, str(kwargs))
        print("<DEBUG> ", msg)

    def debug(self, msg, *args, **kwargs):
        if self.normal_log.isEnabledFor(DEBUG):
            self.normal_log._log(DEBUG, msg, args, **kwargs)
            self._backup_print(msg, args, kwargs)

    def info(self, msg, *args, **kwargs):
        if self.normal_log.isEnabledFor(INFO):
            self.normal_log._log(INFO, msg, args, **kwargs)
            self._backup_print(msg, args, kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.normal_log.isEnabledFor(WARN):
            self.normal_log._log(WARNING, msg, args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        if self.normal_log.isEnabledFor(WARN):
            self.normal_log._log(WARN, msg, args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.error_log.isEnabledFor(ERROR):
            self.normal_log._log(ERROR, msg, args, **kwargs)
            self.error_log._log(ERROR, msg, args, **kwargs)
        print(msg, args, kwargs)

    def critical(self, msg, *args, **kwargs):
        if self.error_log.isEnabledFor(CRITICAL):
            self.normal_log._log(CRITICAL, msg, args, **kwargs)
            self.error_log._log(CRITICAL, msg, args, **kwargs)

    def fatal(self, msg, *args, **kwargs):
        if self.error_log.isEnabledFor(FATAL):
            self.normal_log._log(FATAL, msg, args, **kwargs)
            self.error_log._log(FATAL, msg, args, **kwargs)


logger = ObLog()
