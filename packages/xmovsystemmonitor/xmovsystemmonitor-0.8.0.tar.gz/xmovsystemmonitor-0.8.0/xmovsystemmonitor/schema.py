# coding: utf-8

from typing import List
from dataclasses import dataclass
import time

from .psutil_helper import get_cpu_percent, get_memory_percent


@dataclass
class Arguments:
    host: str = "0.0.0.0"
    port: int = 8000
    max_num: int = 3000
    interval: float = 1.0

    def to_dict(self):
        return {
            "host": self.host,
            "port": self.port,
            "max_num": self.max_num,
            "interval": self.interval,
        }

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
        self.system_info_list: List[SystemInfo] = []
        self.max_system_info_list_length = max_system_info_list_length

    @property
    def total_length(self) -> int:
        return len(self.system_info_list)

    @property
    def latest_system_info(self) -> SystemInfo:
        return self.system_info_list[-1] if self.system_info_list else None

    def collect(self) -> SystemInfo:
        system_info = SystemInfo(
            get_cpu_percent(), get_memory_percent(), time.time())
        self.system_info_list.append(system_info)
        if len(self.system_info_list) > self.max_system_info_list_length:
            self.system_info_list.pop(0)
        return system_info

    def get_system_info_list(self) -> List[SystemInfo]:
        return self.system_info_list

    def reset_system_info_list(self) -> None:
        self.system_info_list.clear()

    def statistic(self) -> dict:
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
