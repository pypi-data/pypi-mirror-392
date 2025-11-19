# xmovsystemmonitor

一个用于监测系统CPU和内存使用率的工具，提供HTTP API接口，可以用于监控系统性能（内存、CPU）。

## Features


## 安装

```bash
# 本地
pip install xmovsystemmonitor -i https://pypi.org/simple/
# 阿里云
pip install xmovsystemmonitor -i http://pypi.aliyun.com/simple/
```

## 用法

```bash
# 服务端，被监测端运行此命令
python -m xmovsystemmonitor 
# 指定主机和端口, 并指定最大记录数量
python -m xmovsystemmonitor --host 0.0.0.0 --port 8000 --max-num 3000
```

测试代码，可以运行在本地，也可以运行在远程服务器上。
```python
from xmovsystemmonitor.client.client import Client
import time

client = Client()
client.start()  # 启动监控, 启动后会立即开始采集数据， 每次start会清空之前采集的数据
time.sleep(10)  # 睡眠10秒
client.stop()  # 停止监控, 停止后会立即停止采集数据， 并抓取统计信息
cpu_min = client.cpu.min
cpu_max = client.cpu.max
cpu_avg = client.cpu.avg
memory_min = client.memory.min
memory_max = client.memory.max
memory_avg = client.memory.avg
```

## 开发测试
```python
import pytest
import requests
import json
from functools import partial

json_dump = partial(json.dumps, indent=4, ensure_ascii=False)


def test_get_system_info():
    response = requests.get("http://localhost:8000/")
    print(response.json())
    assert response.status_code == 200
    assert "cpu_percent" in response.json()
    assert "memory_percent" in response.json()

def test_start_monitoring():
    response = requests.get("http://localhost:8000/start-monitoring")
    print(response.json())
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "监控已启动"

def test_stop_monitoring():
    response = requests.get("http://localhost:8000/stop-monitoring")
    print(response.json())
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "监控已停止"

def test_statistic():
    response = requests.get("http://localhost:8000/statistic")
    print(json_dump(response.json()))
    assert response.status_code == 200
    assert "cpu_percent" in response.json()
    assert "memory_percent" in response.json()
    assert "data_list" in response.json()

```


### 开发配置

```bash
# 克隆仓库
git clone git@github.com:atanx/xmovsystemmonitor.git
cd xmovsystemmonitor

# 安装开发依赖
pip install -e ".[dev]"

# 手动修改修改__init__.py中的__version__， 然后打包
make build

# 上传到xmov-pypi, 需要安装twine， 配置~/.pypirc
make upload
```

    