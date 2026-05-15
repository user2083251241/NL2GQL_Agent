"""
SSE 流式接口测试脚本

模拟前端通过 SSE 接收 LangChain Agent 的推理链输出
只打印后端返回的原始数据，不添加任何自定义输出
"""
import requests
import json
import sys


def test_sse_stream(query: str = "id为1的电影叫什么？"):
    """
    测试 SSE 流式接口
    """
    url = "http://127.0.0.1:5000/api/graph-agent/query/stream"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {
        "query": query,
        "timestamp": 1234567890,
        "enable_self_correction": True
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            stream=True,
            timeout=300
        )
        
        if response.status_code != 200:
            print(f"错误: HTTP {response.status_code}")
            print(response.text)
            return
        
        # 逐行读取 SSE 数据，实时打印
        buffer = ""
        step_count = 0
        
        print("开始接收流式数据...\n")
        
        for line in response.iter_lines(decode_unicode=True, delimiter='\n'):
            if line is None:
                continue
            
            # 累积到buffer
            buffer += line + "\n"
            
            # 如果遇到空行，说明一个完整事件结束
            if line == "":
                # 处理完整的事件
                if buffer.startswith("data: "):
                    try:
                        data_str = buffer[6:].strip()  # 去掉 "data: " 前缀和空白
                        if data_str:
                            data = json.loads(data_str)
                            
                            # 判断是否为最终答案（与非流式接口格式一致）
                            if data.get('success') and 'answer' in data:
                                print('\n========== 最终答案 ==========')
                                print(f'问题: {data.get("question", "")}')
                                print(f'答案: {data["answer"]}')
                                print(f'时间戳: {data.get("timestamp", "")}')
                                print('================================\n')
                                sys.stdout.flush()
                                continue  # 跳过后续处理
                            
                            # 将所有类型的步骤都添加到推理链中
                            if data.get('type') and data.get('content'):
                                step_count += 1
                                
                                # 实时打印每个步骤
                                print(f"[步骤 {step_count}]")
                                print(data["content"])
                                print("-" * 60)
                                
                                # 强制刷新输出缓冲区
                                sys.stdout.flush()
                    except json.JSONDecodeError:
                        pass  # 忽略解析错误
                
                # 重置buffer
                buffer = ""
        
        print(f"\n✅ 总共接收到 {step_count} 个步骤")
        
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器", file=sys.stderr)
    except requests.exceptions.Timeout:
        print("错误: 请求超时", file=sys.stderr)
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "id为1的电影叫什么？"
    
    test_sse_stream(query)
