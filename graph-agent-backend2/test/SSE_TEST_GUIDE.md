# SSE 流式接口测试指南

## 测试脚本

### test_sse_stream.py

模拟前端通过 SSE 接收 LangChain Agent 的推理链输出。

**特点**：
- ✅ 只打印后端返回的原始 content 内容
- ✅ 不添加任何自定义输出、emoji 或格式化
- ✅ 完全模拟前端的流式读取行为

## 使用方法

### 1. 启动后端服务

```bash
python run.py
```

确保后端服务运行在 `http://127.0.0.1:5000`

### 2. 运行测试脚本

**使用默认查询**：
```bash
python test/test_sse_stream.py
```

**使用自定义查询**：
```bash
python test/test_sse_stream.py "查询评分最高的电影"
```

### 3. 观察输出

脚本会实时打印从后端接收到的推理链步骤，例如：

```
测试查询: id为1的电影叫什么？

============================================================

Thought: 我需要获取数据库的Schema信息...

Action: execute_gremlin
Action Input: {"gremlin": "g.V().has('Movie', 'movieId', 1).values('title')"}

✅ 查询成功
   结果数量: 1
   数据: ['Toy Story (1995)']

Final Answer: ID 为 1 的电影叫 Toy Story (1995)。


总共接收到 4 个步骤
```

## 验证要点

1. **实时性**：每个步骤应该逐步出现，而不是等全部完成后一次性显示
2. **完整性**：应该包含 Thought → Action → Observation → Final Answer 的完整链路
3. **格式一致性**：输出应该与后端终端显示的 Agent 推理链一致
4. **无额外输出**：不应该有 emoji、颜色代码或其他装饰（除非是 LLM 生成的原始内容）

## 故障排查

### 连接失败
```
错误: 无法连接到服务器，请确保后端服务正在运行
```
**解决**：确保后端 Flask 服务已启动并监听 5000 端口

### 请求超时
```
错误: 请求超时
```
**解决**：检查网络连接，或增加脚本中的 timeout 参数

### JSON 解析错误
```
JSON 解析错误: ...
```
**解决**：检查后端是否正确返回 SSE 格式的数据

## 技术细节

- **协议**：SSE (Server-Sent Events)
- **Content-Type**：text/event-stream
- **数据格式**：`data: {"type": "...", "content": "...", "timestamp": 123}\n\n`
- **流式读取**：使用 `requests.post(stream=True)` + `iter_lines()`
