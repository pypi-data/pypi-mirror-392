# coding: utf-8

import pytest
import asyncio
import aiohttp
from xmovsystemmonitor.client.async_client import AsyncClient

client = AsyncClient()


@pytest.mark.asyncio
async def start():
    await client.start()       


@pytest.mark.asyncio
async def stop():
    await asyncio.sleep(5)
    await client.stop()


@pytest.mark.asyncio
async def test_async_client():
    await client._ensure_session()
    task1 = asyncio.create_task(start())
    task2 = asyncio.create_task(stop())
    result = await asyncio.gather(task1, task2)
    await client._close_session()
    assert client.statistic is not None
    print(client.statistic.to_dict())
    print(f"cpu_min: {client.cpu.min}, cpu_max: {client.cpu.max}, cpu_avg: {client.cpu.avg}")
    print(f"memory_min: {client.memory.min}, memory_max: {client.memory.max}, memory_avg: {client.memory.avg}")