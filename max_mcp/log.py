#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      : 2022/06/24 10:18
# Author    : LiuYang
# Usage     : 
# Version   :
# Comment   :

"""
日志类


%(levelname)s: 打印日志级别名称

%(pathname)s: 打印当前执行程序的路径，其实就是sys.argv[0]

%(filename)s: 打印当前执行程序名

%(funcName)s: 打印日志的当前函数

%(lineno)d: 打印日志的当前行号

%(asctime)s: 打印日志的时间

%(thread)d: 打印线程ID

%(threadName)s: 打印线程名称

%(process)d: 打印进程ID

%(message)s: 打印日志信息

"""

# Import built-in modules
import os
import logging
import threading
import logging.handlers
import tempfile
import sys
from datetime import datetime
# Import third-party modules
from six import string_types
# Import local modules


__all__ = ["LogManager", "log_file"]

ROOT_LOG_NAME = "tmtk"

LOG_SIZE = 1024 * 1024 * 100
BACKUP_COUNT = 10

FORMAT_STR = ""


def _get_temp_log_file_path():
    """find a temp log file path for logger"""

    temp_dir = tempfile.gettempdir()
    date_code = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(temp_dir, "dcc_mcp_%s.log" % date_code).replace("\\", "/")


def _remove_handlers_from_logger(logger, handler_type):
    """remove specific handler type form logger

    Args:
        logger:
        handler_type:

    Returns:

    """
    for handler in logger.handlers:
        if isinstance(handler, handler_type):
            logger.removeHandler(handler)


def _add_stream_handler(logger):
    """add a stream handler to logger

    Args:
        logger:

    Returns:

    """
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(FORMAT_STR)
    formatter.datefmt = '%H:%M:%S'
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


def _create_logger(logger_name):
    """创建logger, 创建之后，清空所有的handler, 因为经常出现重复输出的现象

    Args:
        logger_name:

    Returns:

    """
    logger = logging.getLogger(logger_name)
    handlers = logger.handlers
    for handler in handlers:
        logger.removeHandler(handler)
    return logger


def _add_rotating_file_handler(logger, log_file):
    """add rotating file handler to a logger

    Args:
        logger:
        log_file:

    Returns:

    """
    _remove_handlers_from_logger(logger, logging.handlers.RotatingFileHandler)

    log_dir = os.path.dirname(log_file)
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    handler = logging.handlers.RotatingFileHandler(log_file,
                                                   maxBytes=LOG_SIZE,
                                                   backupCount=BACKUP_COUNT)
    formatter = logging.Formatter(FORMAT_STR)
    formatter.datefmt = '%H:%M:%S'
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class Logger(object):
    def __init__(self, logger):
        self.logger = logger

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message, send_to_tm=True):
        """
        错误信息
        Args:
            message:
            send_to_tm: <bool> 是否上传 Teamones

        Returns:

        """
        self.logger.error(message)

    def success(self, message):
        self.logger.success(message)


class LogManager(object):
    _lock = threading.Lock()
    _has_inited = False

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not hasattr(cls, "_instance"):
                instance = super(LogManager, cls).__new__(cls, *args, **kwargs)
                cls._instance = instance
        return cls._instance

    @staticmethod
    def get_logger(logger_name, logger_path=None, log_file="", level=logging.DEBUG, force_write=True):
        """get a logger instance

        Args:
            logger_name(str): 当前log名
            logger_path(str): 当前log所处的filepath.
            log_file(str): log 存放文件路径
            level(logging.DEBUG): log 默认 bug 等级
            force_write(bool): 是否强制写出到temp 路径

        Returns:

        """
        # 判断当前环境是否在Unreal下
        global FORMAT_STR
        if logger_path:
            FORMAT_STR = "%(asctime)s - %(name)-3s - {} - %(levelname)-5s \n\t%(message)s\n".format(logger_path.replace("\\", "/"))
        else:
            FORMAT_STR = "%(asctime)s - %(name)-3s - %(filename)s - %(levelname)-5s \n\t%(message)s\n"
        log_file = log_file.replace("\\", "/")

        if not isinstance(logger_name, string_types):
            raise TypeError("Logger name must be string or unicode")

        # create logger
        logger = _create_logger(logger_name)
        logger.setLevel(level)
        logger.propagate = False
        _add_stream_handler(logger)

        # default write out to temp file.
        if not log_file:
            if force_write:
                log_file = _get_temp_log_file_path()

        if log_file:
            _add_rotating_file_handler(logger, log_file)

        return Logger(logger)


log_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../3dsMaxMCPServer.log"))

if __name__ == "__main__":
    for i in range(5):
        log = LogManager.get_logger(__name__, "vvvv")
        log.error("child%s" % i)

