"""
测试执行查询任务时大模型消耗的token数量
"""
import requests
import time
import json


def test_token_consumption():
    """测试查询任务的token消耗"""
    
    url = "http://localhost:5000/api/graph-agent/query"
    
    test_queries = [
        "数据库中总共有多少部电影？",
        "动作类型的电影有哪些？"
    ]
    
    total_tokens = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_cost_usd = 0.0
    successful_requests = 0
    
    print("=" * 80)
    print("测试大模型Token消耗")
    print("=" * 80 + "\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"[{i}/{len(test_queries)}] 查询: {query}")
        
        payload = {
            "query": query,
            "timestamp": int(time.time()),
            "enable_self_correction": True
        }
        
        try:
            start_time = time.time()
            response = requests.post(url, json=payload, timeout=120)
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    token_usage = data.get("token_usage", {})
                    
                    prompt_tokens = token_usage.get("prompt_tokens", 0)
                    completion_tokens = token_usage.get("completion_tokens", 0)
                    tokens = token_usage.get("total_tokens", 0)
                    cost_usd = token_usage.get("estimated_cost_usd", 0.0)
                    
                    total_prompt_tokens += prompt_tokens
                    total_completion_tokens += completion_tokens
                    total_tokens += tokens
                    total_cost_usd += cost_usd
                    successful_requests += 1
                    
                    print(f"  ✅ 成功")
                    print(f"  ⏱️  耗时: {elapsed_time:.2f}秒")
                    print(f"  📊 Token使用:")
                    print(f"     - Prompt: {prompt_tokens}")
                    print(f"     - Completion: {completion_tokens}")
                    print(f"     - 总计: {tokens}")
                    if cost_usd > 0:
                        print(f"     - 预估费用: ${cost_usd:.6f}")
                else:
                    print(f"  ❌ 失败: {data.get('error', '未知错误')}")
            else:
                print(f"  ❌ HTTP错误: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("  ❌ 连接失败，请确认后端服务正在运行")
            return
        except requests.exceptions.Timeout:
            print("  ❌ 请求超时")
        except Exception as e:
            print(f"  ❌ 异常: {str(e)}")
        
        print()
    
    # 输出汇总
    print("=" * 80)
    print("测试汇总")
    print("=" * 80)
    print(f"总请求数: {len(test_queries)}")
    print(f"成功请求数: {successful_requests}")
    print(f"\n📊 Token消耗统计:")
    print(f"  - 总Prompt Tokens: {total_prompt_tokens}")
    print(f"  - 总Completion Tokens: {total_completion_tokens}")
    print(f"  - 总Tokens: {total_tokens}")
    print(f"  - 平均Tokens/查询: {total_tokens/successful_requests:.1f}" if successful_requests > 0 else "  - 平均Tokens/查询: N/A")
    print(f"\n💰 预估费用:")
    print(f"  - 总计: ${total_cost_usd:.4f}")
    print(f"  - 平均/查询: ${total_cost_usd/successful_requests:.6f}" if successful_requests > 0 else "  - 平均/查询: N/A")


if __name__ == "__main__":
    # 检查后端服务是否运行
    print("🔍 检查后端服务状态...")
    try:
        response = requests.get("http://localhost:5000/api/v1", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常运行\n")
        else:
            print(f"⚠️  后端服务状态异常: {response.status_code}\n")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请先启动服务:")
        print("   python run.py")
        exit(1)
    
    test_token_consumption()
    print("\n测试完成！")