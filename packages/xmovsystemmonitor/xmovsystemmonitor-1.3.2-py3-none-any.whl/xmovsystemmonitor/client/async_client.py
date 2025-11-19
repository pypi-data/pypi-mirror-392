# coding: utf-8

import asyncio
import aiohttp
from xmovsystemmonitor.schema import Statistic, CPUStatistic, MemoryStatistic

class AsyncClient:
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.session = None
        self._statistic: Statistic = None
    
    async def _ensure_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def _close_session(self):
        if self.session is not None:
            await self.session.close()

    async def _get_system_info(self):
        async with self.session.get(f"http://{self.host}:{self.port}/") as response:
            return await response.json()
    
    async def _start_monitoring(self):
        async with self.session.get(f"http://{self.host}:{self.port}/start-monitoring") as response:
            return await response.json()
    
    async def _stop_monitoring(self):
        async with self.session.get(f"http://{self.host}:{self.port}/stop-monitoring") as response:
            return await response.json()    
    
    async def _get_statistic(self):
        async with self.session.get(f"http://{self.host}:{self.port}/statistic") as response:
            dat = await response.json()
            self._statistic = Statistic.from_dict(dat)
            return dat
    
    async def start(self):
        await self._start_monitoring()
    
    async def stop(self):
        await self._stop_monitoring()
        await self._get_statistic()
    
    @property
    def statistic(self) -> Statistic:
        return self._statistic
    
    @property
    def cpu(self) -> CPUStatistic:
        return self._statistic.cpu
    
    @property
    def memory(self) -> MemoryStatistic:
        return self._statistic.memory
    