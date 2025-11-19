# coding: utf-8

import logging

def get_logger(name: str, level: int = logging.INFO, filename: str = "systemmonitor.log"):
    """
    获取一个日志记录器，可以用于记录系统监控信息。

    Args:
        name: 日志记录器名称
        level: 日志记录器级别，默认INFO
        filename: 日志记录文件名，默认"systemmonitor.log"
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(filename) if filename != "" else None
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


logger = get_logger(__name__, level=logging.INFO, filename="systemmonitor.log")