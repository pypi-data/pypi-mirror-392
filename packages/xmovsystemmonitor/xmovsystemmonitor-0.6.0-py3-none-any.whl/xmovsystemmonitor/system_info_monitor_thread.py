# coding: utf-8

import threading
import time
import logging
from dataclasses import dataclass

from starlette.background import P
from .system_info import get_cpu_percent, get_memory_percent
from xmovsystemmonitor.logger import logger

@dataclass
class SystemInfo:
    cpu_percent: float
    memory_percent: float
    timestamp: float

    def to_dict(self):
        return {
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "timestamp": self.timestamp,
        }


class SystemInfoCollector:
    def __init__(self, max_system_info_list_length: int = 3000):
        self.system_info_list =[]
        self.max_system_info_list_length = max_system_info_list_length

    @property
    def total_length(self):
        return len(self.system_info_list)

    @property
    def latest_system_info(self):
        return self.system_info_list[-1] if self.system_info_list else None

    def collect(self):
        system_info = SystemInfo(get_cpu_percent(), get_memory_percent(), time.time())
        self.system_info_list.append(system_info)
        if len(self.system_info_list) > self.max_system_info_list_length:
            self.system_info_list.pop(0)
        return system_info
    
    def get_system_info_list(self):
        return self.system_info_list
    
    def reset_system_info_list(self):
        self.system_info_list.clear()

    def statistic(self):
        return {
            "cpu_percent": {
                "min": min(system_info.cpu_percent for system_info in self.system_info_list),
                "max": max(system_info.cpu_percent for system_info in self.system_info_list),
                "avg": sum(system_info.cpu_percent for system_info in self.system_info_list) / len(self.system_info_list),
            },
            "memory_percent": {
                "min": min(system_info.memory_percent for system_info in self.system_info_list),
                "max": max(system_info.memory_percent for system_info in self.system_info_list),
                "avg": sum(system_info.memory_percent for system_info in self.system_info_list) / len(self.system_info_list),
            },
            "data_list": [system_info.to_dict() for system_info in self.system_info_list],
        }


class SystemInfoMonitorThread(threading.Thread):
    def __init__(self, interval: float = 1.0, max_system_info_list_length: int = 3000):
        super().__init__()
        self.running = False
        self.interval = interval
        self.max_system_info_list_length = max_system_info_list_length
        self.system_info_collector = SystemInfoCollector()

    def run(self):
        while True:
            if not self.running:
                time.sleep(self.interval)
                logger.info("监控暂停中...")
                continue
            latest_system_info = self.system_info_collector.collect()
            logger.info(f"监控中, 最新系统信息: {latest_system_info.to_dict()}, 系统信息列表长度: {self.system_info_collector.total_length}")
            time.sleep(self.interval)
    
    def start_to_monitor(self):
        self.running = True
        logger.info("监控已重置，开始监控")
    
    def reset_system_info_list(self):
        self.system_info_collector.reset_system_info_list()
    
    def stop_to_monitor(self):
        self.running = False
        logger.info("监控已停止")
    
    def statistic(self):
        return self.system_info_collector.statistic()
