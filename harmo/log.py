#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Created by hubiao on 2017/5/12

import logging
import os
import time

LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

logger = logging.getLogger()
level = 'default'

def create_file(filename):
    path = filename[0:filename.rfind('/')]
    if not os.path.isdir(path):
        os.makedirs(path)
    if not os.path.isfile(filename):
        fd = open(filename, mode='w', encoding='utf-8')
        fd.close()
    else:
        pass

def set_handler(levels):
    if levels == 'error':
        logger.addHandler(MyLog.err_handler)
    logger.addHandler(MyLog.handler)

def remove_handler(levels):
    if levels == 'error':
        logger.removeHandler(MyLog.err_handler)
    logger.removeHandler(MyLog.handler)

def get_current_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

class MyLog:
    date_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    dirname = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/logs/" + date_time
    log_file = dirname+'/log.log'
    err_file = dirname+'/err.log'
    create_file(log_file)
    create_file(err_file)
    logger.setLevel(LEVELS.get(level, logging.NOTSET))

    handler = logging.FileHandler(log_file, encoding='utf-8')
    err_handler = logging.FileHandler(err_file, encoding='utf-8')

    @staticmethod
    def debug(log_msg):
        set_handler('debug')
        logger.debug("[" + get_current_time() + "][DEBUG]: " + log_msg)
        remove_handler('debug')

    @staticmethod
    def info(log_msg):
        set_handler('info')
        logger.info("[" + get_current_time() + "][INFO]: " + log_msg)
        remove_handler('info')

    @staticmethod
    def warning(log_msg):
        set_handler('warning')
        logger.warning("[" + get_current_time() + "][WARNING]: " + log_msg)
        remove_handler('warning')

    @staticmethod
    def error(log_msg):
        set_handler('error')
        logger.error("[" + get_current_time() + "][ERROR]: " + log_msg)
        remove_handler('error')

    @staticmethod
    def critical(log_msg):
        set_handler('critical')
        logger.error("[" + get_current_time() + "][CRITICAL]: " + log_msg)
        remove_handler('critical')


if __name__ == "__main__":
    MyLog.debug("This is debug message")
    MyLog.info("This is info message")
    MyLog.warning("This is warning message")
    MyLog.error("This is error")
    MyLog.critical("This is critical message")
