
import psutil


def get_cpu_percent(interval: float = 1.0) -> float:
    """
    获取CPU使用率百分比
    
    Args:
        interval: 采样间隔时间（秒），默认1秒
        
    Returns:
        CPU使用率百分比（0-100）
    """
    return psutil.cpu_percent(interval=interval)


def get_memory_percent() -> float:
    """
    获取内存使用率百分比
    
    Returns:
        内存使用率百分比（0-100）
    """
    return psutil.virtual_memory().percent


def get_system_info() -> dict:
    """
    获取系统信息（CPU和内存使用率）
    
    Returns:
        包含CPU和内存使用率的字典
    """
    return {
        "cpu_percent": get_cpu_percent(),
        "memory_percent": get_memory_percent(),
    }
