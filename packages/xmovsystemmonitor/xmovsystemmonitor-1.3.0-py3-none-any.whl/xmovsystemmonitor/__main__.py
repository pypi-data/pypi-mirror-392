"""命令行入口 - 显示系统监控信息"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import argparse
from xmovsystemmonitor.system_info_monitor_thread import SystemInfoMonitorThread
from xmovsystemmonitor.psutil_helper import get_system_info
from xmovsystemmonitor.schema import Arguments

from xmovsystemmonitor.logger import logger
from xmovsystemmonitor import __version__

def get_args() -> Arguments:
    """获取命令行参数"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--max-num", type=int, default=3000, help="最大系统信息数量")
    parser.add_argument("--interval", type=float, default=1.0, help="采集间隔时间")
    args = parser.parse_args()
    args = Arguments(
        host=args.host,
        port=args.port,
        max_num=args.max_num,
        interval=args.interval,
    )
    return args

args = get_args()

app = FastAPI()
background_thread = SystemInfoMonitorThread(interval=1.0, max_system_info_list_length=args.max_num)
background_thread.start()

@app.get("/")
def read_root():
    info = get_system_info()
    return JSONResponse(content=info)

@app.get("/start-monitoring")
def start_monitoring():
    """启动监控API"""
    background_thread.reset_system_info_list()
    background_thread.start_to_monitor()
    return JSONResponse(content={"message": "监控已启动"})

@app.get("/stop-monitoring")
def stop_monitoring():
    """停止监控API"""
    background_thread.stop_to_monitor()
    return JSONResponse(content={"message": "监控已停止"})

@app.get("/statistic")
def statistic():
    """获取监控统计信息API"""
    return JSONResponse(content=background_thread.statistic())

if __name__ == "__main__":
    logger.info(f"xmovsystemmonitor version: {__version__}")
    uvicorn.run(app, host=args.host, port=args.port)
