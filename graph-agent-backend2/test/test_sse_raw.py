"""
SSE 流式接口原始响应测试

直接打印后端返回的原始数据，不做任何解析
"""
import requests
import sys


def test_raw_response(query: str = "id为1的电影叫什么？"):
    """
    测试 SSE 流式接口的原始响应
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
        
        print(f"HTTP Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}\n")
        
        # 逐块读取并打印原始内容
        byte_count = 0
        for chunk in response.iter_content(chunk_size=256):
            if chunk:
                byte_count += len(chunk)
                text = chunk.decode('utf-8', errors='ignore')
                print(text, end='', flush=True)
                
                # 限制输出长度
                if byte_count > 5000:
                    print("\n\n[输出已截断...]")
                    break
        
        print(f"\n\n总字节数: {byte_count}")
        
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "id为1的电影叫什么？"
    
    test_raw_response(query)
