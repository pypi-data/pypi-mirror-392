# coding: utf-8

import time
import threading
from xmovsystemmonitor.logger import logger
from xmovsystemmonitor.schema import SystemInfoCollector


class SystemInfoMonitorThread(threading.Thread):
    def __init__(self, interval: float = 1.0, max_system_info_list_length: int = 3000):
        """
        一个用于监测系统CPU和内存使用率的线程，可以用于监控系统性能（内存、CPU）。

        Args:
            interval: 采集间隔时间（秒），默认1秒
            max_system_info_list_length: 最大系统信息列表长度，默认3000
        """
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
    
    def set_interval(self, interval: float):
        """设置采集间隔时间
        
        Args:
            interval: 采集间隔时间（秒）
        """
        self.interval = interval

    def set_max_system_info_list_length(self, max_system_info_list_length: int):
        """设置最大系统信息列表长度
        
        Args:
            max_system_info_list_length: 最大系统信息列表长度
        """
        self.max_system_info_list_length = max_system_info_list_length

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
