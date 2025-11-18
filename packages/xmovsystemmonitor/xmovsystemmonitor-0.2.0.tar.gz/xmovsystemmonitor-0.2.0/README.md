# xmovsystemmonitor

一个用于xmovsystemmonitor的工具，可以读取xmovsystemmonitor的日志文件，并按照时间顺序执行xmovsystemmonitor请求。

## Features


## 安装

```bash
# 本地
pip install xmovsystemmonitor -i https://pypi.org/simple/
# 阿里云
pip install xmovsystemmonitor -i https://pypi.org/simple/
```

## 用法

```bash
python -m xmovsystemmonitor 
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

    