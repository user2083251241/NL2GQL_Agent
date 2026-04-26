"""
测试Agent查询API端点
"""
import requests
import time
import json


def test_agent_query():
    """测试 /api/graph-agent/query 端点"""
    
    url = "http://localhost:5000/api/graph-agent/query"
    
    # 测试用例1：简单查询
    print("=" * 60)
    print("测试1: 简单查询 - 数据库中总共有多少个顶点？")
    print("=" * 60)
    
    payload = {
        "query": "数据库中总共有多少个顶点？",
        "timestamp": int(time.time())
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        print(f"状态码: {response.status_code}")
        print(f"响应内容:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n")
    
    # 测试用例2：带关系的查询
    print("=" * 60)
    print("测试2: 找出所有在 Tech 行业工作的公司。")
    print("=" * 60)
    
    payload = {
        "query": "找出所有在 Tech 行业工作的公司。",
        "timestamp": int(time.time())
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        print(f"状态码: {response.status_code}")
        print(f"响应内容:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n")
    
    # 测试用例3：缺少必需字段
    print("=" * 60)
    print("测试3: 错误处理 - 缺少query字段")
    print("=" * 60)
    
    payload = {
        "timestamp": int(time.time())
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        print(f"状态码: {response.status_code}")
        print(f"响应内容:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"请求失败: {e}")


if __name__ == "__main__":
    print("开始测试Agent查询API...\n")
    test_agent_query()
    print("\n测试完成！")
