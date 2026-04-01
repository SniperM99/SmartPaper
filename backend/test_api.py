#!/usr/bin/env python3
"""FastAPI 后端测试脚本"""
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"


def test_health():
    """测试健康检查"""
    print("\n🔍 测试健康检查...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    return response.status_code == 200


def test_get_papers():
    """测试获取论文列表"""
    print("\n🔍 测试获取论文列表...")
    response = requests.get(f"{BASE_URL}/api/ingestion/papers")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    return response.status_code == 200


def test_get_analysis_options():
    """测试获取分析选项"""
    print("\n🔍 测试获取分析选项...")
    response = requests.get(f"{BASE_URL}/api/profile/options")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    return response.status_code == 200


def test_get_profile():
    """测试获取科研画像"""
    print("\n🔍 测试获取科研画像...")
    response = requests.get(f"{BASE_URL}/api/profile/profile")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    return response.status_code == 200


def test_research_map_query():
    """测试研究地图查询"""
    print("\n🔍 测试研究地图查询...")
    payload = {
        "query": "transformer 架构",
        "scope": "all",
        "max_results": 5
    }
    response = requests.post(f"{BASE_URL}/api/research-map/query", json=payload)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    return response.status_code == 200


def main():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 SmartPaper FastAPI 后端测试")
    print("=" * 60)

    tests = [
        ("健康检查", test_health),
        ("获取论文列表", test_get_papers),
        ("获取分析选项", test_get_analysis_options),
        ("获取科研画像", test_get_profile),
        ("研究地图查询", test_research_map_query),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {name} - 通过")
            else:
                failed += 1
                print(f"❌ {name} - 失败")
        except Exception as e:
            failed += 1
            print(f"❌ {name} - 异常: {e}")

    print("\n" + "=" * 60)
    print(f"📊 测试结果: 通过 {passed}, 失败 {failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()
