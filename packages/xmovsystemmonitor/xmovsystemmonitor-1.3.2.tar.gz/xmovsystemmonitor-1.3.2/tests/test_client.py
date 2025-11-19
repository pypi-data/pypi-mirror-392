#! /usr/bin/env python3
# coding: utf-8

from xmovsystemmonitor.client.client import Client
import time
import random


def test_client():
    run_count = 3
    while run_count > 0:
        sleep_seconds = random.randint(3, 5)
        print(f"====test client start [sleep_seconds: {sleep_seconds}] ====")
        client = Client()
        client.start() # 启动监控
        time.sleep(sleep_seconds)
        client.stop() # 停止监控
        print(client.statistic.to_dict())
        print(f"cpu_min: {client.cpu.min}, cpu_max: {client.cpu.max}, cpu_avg: {client.cpu.avg}")
        print(f"memory_min: {client.memory.min}, memory_max: {client.memory.max}, memory_avg: {client.memory.avg}")
        print("====test client end====")
        run_count -= 1
