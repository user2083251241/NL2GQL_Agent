# 项目架构说明

## 📁 目录结构

```
.
├── app/                    # 表现层 (Presentation Layer)
│   └── api/
│       └── v1/
│           └── routes.py   # API路由定义
│
├── services/               # 业务逻辑层 (Business Logic Layer) ⭐ 新增
│   ├── agents/             # AI智能体业务
│   │   ├── agent.py        # GraphQueryAgent核心逻辑
│   │   ├── tools.py        # Agent工具定义
│   │   └── prompts.py      # Prompt模板
│   └── queries/            # 专业查询业务
│       └── direct_query.py # 直接Gremlin查询服务
│
├── modules/                # 基础设施层 (Infrastructure Layer)
│   ├── database/           # 数据库访问模块
│   │   └── client.py       # HugeGraph客户端封装
│   └── llm/                # LLM访问模块
│       └── client.py       # ChatOpenAI客户端封装
│
├── scripts/                # 脚本工具
│   └── generate_test_data.py  # 测试数据生成器
│
├── config.py               # 全局配置
├── run.py                  # 应用启动入口
└── test_*.py              # 单元测试文件
```

## 🏗️ 分层架构

### 1. 表现层 (`app/`)
- **职责**: 处理HTTP请求和响应
- **组件**: Flask蓝图、API路由
- **关键文件**: `app/api/v1/routes.py`

### 2. 业务逻辑层 (`services/`) ⭐
- **职责**: 实现核心业务规则和流程
- **子模块**:
  - `agents/`: AI智能体相关业务（自然语言查询）
  - `queries/`: 专业查询业务（直接Gremlin执行）
- **设计原则**: 
  - 每个子模块专注于特定业务领域
  - 可独立测试和扩展
  - 不直接依赖Web框架

### 3. 基础设施层 (`modules/`)
- **职责**: 封装外部系统交互
- **子模块**:
  - `database/`: HugeGraph数据库客户端
  - `llm/`: 大语言模型客户端
- **设计原则**:
  - 提供清晰的抽象接口
  - 单例模式管理资源
  - 隐藏实现细节

## 🔄 调用链

```
前端请求
  ↓
app/api/v1/routes.py (表现层)
  ↓
services/agents/ 或 services/queries/ (业务逻辑层)
  ↓
modules/database/ 或 modules/llm/ (基础设施层)
  ↓
外部服务 (HugeGraph, OpenAI API)
```

## 📌 关键API端点

### 1. 自然语言查询
- **路径**: `POST /api/v1/query`
- **用途**: 通过自然语言查询图数据库
- **处理流程**: 
  ```
  用户问题 → GraphQueryAgent → Gremlin生成 → 执行查询 → 结果解释
  ```

### 2. 直接Gremlin查询
- **路径**: `POST /api/v1/direct-query`
- **用途**: 专业人士直接执行Gremlin查询
- **处理流程**:
  ```
  Gremlin语句 → 安全检查 → DirectQueryService → 执行查询
  ```

## 🔐 安全机制

### 直接查询安全防护
1. **危险关键字过滤**: 阻止`drop`, `config`, `system`等破坏性操作
2. **白名单验证**: 只允许以安全前缀开头的查询
3. **参数化查询**: 支持安全的参数替换
4. **独立API密钥**: 建议为直接查询设置单独的鉴权

## 🚀 开发指南

### 添加新业务模块
1. 在`services/`下创建新子目录
2. 实现业务逻辑类
3. 在`app/api/v1/routes.py`中添加对应路由
4. 编写单元测试

### 扩展现有功能
- **AI能力增强**: 修改`services/agents/`
- **查询优化**: 修改`services/queries/`
- **数据库适配**: 修改`modules/database/`
- **LLM切换**: 修改`modules/llm/`

## ⚠️ 向后兼容

旧导入路径仍然有效（通过代理模块）：
```python
# 旧方式（仍可用，但不推荐）
from modules.database import HugeGraphDB
from langchain_agent.agent import GraphQueryAgent

# 新方式（推荐）
from modules.database.client import HugeGraphDB
from services.agents.agent import GraphQueryAgent
```

## 📝 最佳实践

1. **保持分层清晰**: 不要跨层调用
2. **单一职责**: 每个模块只做一件事
3. **依赖注入**: 通过构造函数传递依赖
4. **错误隔离**: 每层处理自己的异常
5. **安全第一**: 所有外部输入必须验证

---

**最后更新**: 2026-04-22  
**版本**: v2.0 (重构版)
