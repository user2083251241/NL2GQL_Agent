"""
简单的查询效率测试脚本
循环执行同一个查询5次，记录每次的用时并计算平均用时
"""
import requests
import time
import json


def test_query_performance():
    """测试查询性能"""
    # 配置
    url = "http://localhost:5000/api/graph-agent/query"
    query = "Person_0 在哪个公司工作？"  # 可以修改为其他查询
    iterations = 5
    
    print(f"🔍 测试查询: {query}")
    print(f"🔄 执行次数: {iterations}")
    print("-" * 50)
    
    response_times = []
    
    for i in range(iterations):
        payload = {
            "query": query,
            "timestamp": int(time.time())
        }
        
        start_time = time.time()
        try:
            response = requests.post(url, json=payload, timeout=60)
            end_time = time.time()
            
            elapsed_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"✅ 第{i+1}次查询 - 用时: {elapsed_time:.2f}秒")
                    print(f"   结果: {result.get('answer', '无结果')}")
                    response_times.append(elapsed_time)
                else:
                    print(f"❌ 第{i+1}次查询 - 失败: {result.get('error', '未知错误')}")
            else:
                print(f"❌ 第{i+1}次查询 - HTTP错误: {response.status_code}")
                
        except Exception as e:
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"❌ 第{i+1}次查询 - 异常: {str(e)} (用时: {elapsed_time:.2f}秒)")
        
        # 稍微间隔一下，避免过于频繁
        if i < iterations - 1:
            time.sleep(0.5)
    
    print("-" * 50)
    
    # 计算并显示统计结果
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        print(f"📊 性能统计:")
        print(f"   成功次数: {len(response_times)}/{iterations}")
        print(f"   平均用时: {avg_time:.2f}秒")
        print(f"   最快用时: {min_time:.2f}秒")
        print(f"   最慢用时: {max_time:.2f}秒")
    else:
        print("❌ 所有查询都失败了，无法计算平均用时")


if __name__ == "__main__":
    print("🚀 开始查询效率测试...")
    print()
    
    # 检查服务是否可用
    try:
        test_response = requests.get("http://localhost:5000/api/v1", timeout=5)
        if test_response.status_code == 200:
            test_query_performance()
        else:
            print("❌ Flask服务未就绪，请先启动服务: python run.py")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Flask服务，请先启动服务: python run.py")
    except Exception as e:
        print(f"❌ 连接错误: {e}")