# coding: utf-8

import logging

def get_logger(name: str, level: int = logging.INFO, filename: str = "systemmonitor.log"):
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