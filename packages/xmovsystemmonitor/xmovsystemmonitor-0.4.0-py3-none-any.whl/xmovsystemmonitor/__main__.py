"""命令行入口 - 显示系统监控信息"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import argparse
from xmovsystemmonitor.system_info_monitor_thread import SystemInfoMonitorThread
from xmovsystemmonitor import get_system_info

from xmovsystemmonitor.logger import logger


parser = argparse.ArgumentParser()
parser.add_argument("--host", type=str, default="0.0.0.0")
parser.add_argument("--port", type=int, default=8000)
args = parser.parse_args()

app = FastAPI()
background_thread = SystemInfoMonitorThread(interval=1.0)
background_thread.start()

@app.get("/")
def read_root():
    info = get_system_info()
    return JSONResponse(content=info)

@app.get("/start-monitoring")
def start_monitoring():
    """启动监控"""
    background_thread.start_to_monitor()
    return JSONResponse(content={"message": "监控已启动"})

@app.get("/stop-monitoring")
def stop_monitoring():
    """停止监控"""
    background_thread.stop_to_monitor()
    return JSONResponse(content={"message": "监控已停止"})

@app.get("/statistic")
def statistic():
    """获取监控统计信息"""
    return JSONResponse(content=background_thread.statistic())

if __name__ == "__main__":
    uvicorn.run(app, host=args.host, port=args.port)
