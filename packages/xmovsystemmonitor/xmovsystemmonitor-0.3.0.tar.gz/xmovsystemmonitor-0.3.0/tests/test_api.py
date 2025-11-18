import pytest
import requests

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
    print(response.json())
    assert response.status_code == 200
    assert "cpu_percent" in response.json()
    assert "memory_percent" in response.json()
    assert "data_list" in response.json()