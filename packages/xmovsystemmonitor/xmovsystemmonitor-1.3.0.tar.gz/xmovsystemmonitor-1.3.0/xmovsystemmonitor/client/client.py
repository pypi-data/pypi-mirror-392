# coding: utf-8

import requests
from xmovsystemmonitor.schema import Statistic, CPUStatistic, MemoryStatistic

class Client:
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        """ 
        一个用于监控系统性能（内存、CPU）的客户端，可以用于监控系统性能（内存、CPU）。

        Args:
            host: 主机地址
            port: 端口号

        Returns:
            Client: 客户端实例
        
        Example:
            client = Client()
            client.start()  # 启动监控
            time.sleep(10)  # 睡眠10秒
            client.stop()  # 停止监控
            print(client.statistic.to_dict())  # 打印统计信息
            print(f"cpu_min: {client.cpu.min}, cpu_max: {client.cpu.max}, cpu_avg: {client.cpu.avg}")
            print(f"memory_min: {client.memory.min}, memory_max: {client.memory.max}, memory_avg: {client.memory.avg}")
        """
        self.host = host
        self.port = port
        self._statistic: Statistic = None

    def _get_system_info(self):
        response = requests.get(f"http://{self.host}:{self.port}/")
        return response.json()
    
    def _start_monitoring(self):
        response = requests.get(f"http://{self.host}:{self.port}/start-monitoring")
        return response.json()
    
    def _stop_monitoring(self):
        response = requests.get(f"http://{self.host}:{self.port}/stop-monitoring")
        return response.json()
    
    def _get_statistic(self):
        response = requests.get(f"http://{self.host}:{self.port}/statistic")
        dat = response.json()
        self._statistic = Statistic.from_dict(dat)
        return dat
    
    def start(self):
        self._start_monitoring()
    
    def stop(self):
        self._stop_monitoring()
        self._get_statistic()
    
    @property
    def statistic(self) -> Statistic:
        return self._statistic

    @property
    def cpu(self) -> CPUStatistic:
        return self._statistic.cpu

    @property
    def memory(self) -> MemoryStatistic:
        return self._statistic.memory


def main():
    import time
    import random
    client = Client()
    run_count = 3
    while run_count > 0:
        sleep_seconds = random.randint(1, 10)
        print("====start monitoring[sleep_seconds: {sleep_seconds}]====")
        client.start() # 启动监控
        time.sleep(sleep_seconds)
        client.stop() # 停止监控
        print(client.statistic.to_dict())
        print(f"cpu_min: {client.statistic.cpu.min}, cpu_max: {client.statistic.cpu.max}, cpu_avg: {client.statistic.cpu.avg}")
        print(f"memory_min: {client.statistic.memory.min}, memory_max: {client.statistic.memory.max}, memory_avg: {client.statistic.memory.avg}")
        print("====stop monitoring====")
        print('\n\n')
        run_count -= 1


if __name__ == "__main__":
    main()
