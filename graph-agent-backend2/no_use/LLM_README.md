# modules/llm.py 使用说明

## 功能概述

`modules/llm.py` 提供了LangChain ChatOpenAI的工厂函数，支持灵活的配置和重试机制。

---

## 快速开始

### 1. 基础用法

```python
from modules.llm import create_llm

# 创建LLM实例（使用默认配置）
llm = create_llm()

# 使用LLM
response = llm.invoke("你好")
print(response.content)
```

### 2. 自定义参数

```python
from modules.llm import create_llm

# 自定义温度、token数等参数
llm = create_llm(
    model="gpt-4",
    temperature=0.9,      # 更高的创造性
    max_tokens=3000,       # 更长的响应
    verbose=True           # 显示详细日志
)
```

### 3. 使用单例模式

```python
from modules.llm import get_llm

# 获取全局单例（首次调用时创建）
llm = get_llm()

# 再次调用返回同一实例
llm2 = get_llm()
assert llm is llm2  # True
```

### 4. 带重试机制的创建

```python
from modules.llm import create_llm_with_retry

# 自动重试最多3次
llm = create_llm_with_retry(max_retries=3)
```

---

## API参考

### `create_llm(**kwargs)`

创建ChatOpenAI实例。

**参数:**
- `model` (str, 可选): 模型名称，默认从配置读取（如 `gpt-3.5-turbo`）
- `temperature` (float): 温度参数 0-1，默认 0.7
- `max_tokens` (int): 最大生成token数，默认 2000
- `verbose` (bool): 是否输出详细日志，默认从配置读取

**返回:**
- `ChatOpenAI` 实例

**异常:**
- `ValueError`: 如果 OPENAI_API_KEY 未配置

---

### `create_llm_with_retry(max_retries=3, **kwargs)`

创建带重试机制的LLM实例。

**参数:**
- `max_retries` (int): 最大重试次数，默认 3
- `**kwargs`: 传递给 `create_llm` 的参数

**返回:**
- `ChatOpenAI` 实例

**特点:**
- 指数退避重试策略
- 自动测试连接
- 适合不稳定的网络环境

---

### `get_llm(**kwargs)`

获取全局LLM单例实例。

**参数:**
- `**kwargs`: 仅在首次创建时生效，传递给 `create_llm`

**返回:**
- `ChatOpenAI` 实例（单例）

**用途:**
- 避免重复创建LLM实例
- 节省资源和API调用开销

---

### `reset_llm()`

重置全局LLM实例。

**用途:**
- 测试时重新初始化
- 切换配置后重建实例

---

## 配置说明

在 `.env` 文件中配置：

```bash
# OpenAI API密钥（必需）
OPENAI_API_KEY=sk-your-api-key

# 使用的模型（可选）
OPENAI_MODEL=gpt-3.5-turbo

# 自定义API地址（可选，用于国内中转）
OPENAI_BASE_URL=https://api.xxx.com/v1

# LangChain详细日志（可选）
LANGCHAIN_VERBOSE=False
```

---

## 使用示例

### 示例1: 简单对话

```python
from modules.llm import create_llm

llm = create_llm()

# 单次对话
response = llm.invoke("什么是图数据库？")
print(response.content)
```

### 示例2: 多轮对话

```python
from modules.llm import create_llm
from langchain_core.messages import HumanMessage, AIMessage

llm = create_llm()

messages = [
    HumanMessage(content="你好"),
    AIMessage(content="你好！有什么可以帮助你的？"),
    HumanMessage(content="请介绍HugeGraph")
]

response = llm.invoke(messages)
print(response.content)
```

### 示例3: 在Agent中使用

```python
from modules.llm import get_llm
from modules.database import get_db
from langchain_agent.agent import GraphQueryAgent

# 获取LLM和数据库实例
llm = get_llm()
db = get_db()

# 创建Agent
agent = GraphQueryAgent(llm=llm, db=db)

# 处理查询
result = agent.process_query("查找所有名字为张三的人")
print(result)
```

---

## 常见问题

### Q1: 提示 "OPENAI_API_KEY 未配置"

**解决方案:**
1. 检查 `.env` 文件是否存在
2. 确认 `OPENAI_API_KEY` 已正确填写
3. 重启Python进程使环境变量生效

### Q2: 使用国内API中转

**解决方案:**
在 `.env` 中设置：
```bash
OPENAI_BASE_URL=https://your-proxy.com/v1
OPENAI_API_KEY=your-proxy-api-key
```

### Q3: 如何切换模型？

**方案1:** 修改 `.env` 中的 `OPENAI_MODEL`  
**方案2:** 创建时指定：
```python
llm = create_llm(model="gpt-4")
```

---

## 测试

运行测试脚本验证功能：
```bash
python test_llm.py
```

预期输出：
```
============================================================
🚀 开始LLM模块完整测试
============================================================

1️⃣ 创建LLM实例...
✅ LLM初始化成功: gpt-3.5-turbo (temperature=0.7)
✅ LLM实例创建成功: gpt-3.5-turbo

2️⃣ 测试LLM连接和响应...
✅ LLM响应成功:
   图数据库是一种使用图结构存储和查询数据的NoSQL数据库...

...
```
