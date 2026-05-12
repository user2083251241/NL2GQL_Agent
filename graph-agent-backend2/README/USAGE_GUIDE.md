# 重构后使用指南

## 🎉 重构完成！

项目已成功重构为标准的三层架构，现在更加模块化、可扩展且易于维护。

## 📋 快速开始

### 1. 验证重构结果

```bash
# 运行验证脚本
python verify_refactoring.py
```

预期输出：
```
✅ 所有验证通过！重构成功！
```

### 2. 启动服务

```bash
# 激活虚拟环境
.venv\Scripts\activate  # Windows

# 启动Flask应用
python run.py
```

### 3. 测试API端点

#### 测试1: 自然语言查询
```bash
curl http://localhost:5000/api/v1/query \
  -X POST \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"找出所有人物\", \"max_retries\": 2}"
```

#### 测试2: 直接Gremlin查询（新增）⭐
```bash
curl http://localhost:5000/api/v1/direct-query \
  -X POST \
  -H "Content-Type: application/json" \
  -d "{\"gremlin\": \"g.V().limit(5)\"}"
```

## 🏗️ 新架构概览

```
graph-agent-backend2/
├── app/                    # 表现层
│   └── api/v1/routes.py   # API路由（2个端点）
│
├── services/               # 业务逻辑层 ⭐ 新增
│   ├── agents/            # AI智能体业务
│   │   ├── agent.py       # GraphQueryAgent
│   │   ├── tools.py       # Agent工具
│   │   └── prompts.py     # Prompt模板
│   └── queries/           # 专业查询业务 ⭐ 新增
│       └── direct_query.py # DirectQueryService
│
├── modules/                # 基础设施层
│   ├── database/          # 数据库模块
│   │   └── client.py      # HugeGraphDB
│   └── llm/               # LLM模块
│       └── client.py      # ChatOpenAI
│
└── scripts/                # 工具脚本
    └── generate_test_data.py
```

## 🧠 Schema映射表集成

### 功能说明
智能体现在集成了 MovieLens 数据集的 schema 映射表，能够：
- 自动加载英文标签到中文语义的映射关系
- 在获取数据库 schema 时自动增强中文语义说明
- 提供字段中文映射速查表，帮助大模型更好地理解数据含义

### 映射表位置
- JSON 格式映射表：`mapping/schema_mapping.json`
- 简化 Markdown 版本：`ml-latest-small/schema_mapping_simple.md`

### 使用效果
当智能体调用 `get_schema_info` 工具时，返回的 schema 信息将包含：
1. **顶点/边标签的中文描述**：如 `User [中文: 用户]`
2. **字段中文映射速查表**：提供所有字段的中文含义对照

这显著增强了智能体对自然语言查询的理解能力，使其能够更准确地将用户问题映射到正确的数据库结构。