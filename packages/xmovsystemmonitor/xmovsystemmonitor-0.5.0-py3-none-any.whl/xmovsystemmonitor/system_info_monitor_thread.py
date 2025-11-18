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
    def __init__(self):
        self.system_info_list =[]
    
    def collect(self):
        self.system_info_list.append(SystemInfo(get_cpu_percent(), get_memory_percent(), time.time()))
    
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
    def __init__(self, interval: float = 1.0):
        super().__init__()
        self.running = False
        self.interval = interval
        self.system_info_collector = SystemInfoCollector()

    def run(self):
        while True:
            if not self.running:
                time.sleep(self.interval)
                logger.info("监控暂停中...")
                continue
            self.system_info_collector.collect()
            latest_system_info: SystemInfo = self.system_info_collector.get_system_info_list()[-1]
            logger.info(f"监控中, 系统信息: {latest_system_info.to_dict()}")
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
