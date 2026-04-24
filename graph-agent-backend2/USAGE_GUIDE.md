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

## 🔌 API端点详解

### 端点1: `/api/v1/query` - 自然语言查询

**用途**: 通过自然语言查询图数据库（适合普通用户）

**请求**:
```json
POST /api/v1/query
{
  "question": "找出所有在北京工作的软件工程师",
  "max_retries": 2
}
```

**响应**:
```json
{
  "success": true,
  "question": "找出所有在北京工作的软件工程师",
  "result": [
    {"name": "张伟", "age": 28, "job_title": "软件工程师"},
    {"name": "李娜", "age": 32, "job_title": "软件工程师"}
  ],
  "explanation": "查询找到了2位在北京工作的软件工程师...",
  "gremlin": "g.V().has('city', '北京').has('job_title', '软件工程师')",
  "retries": 1
}
```

**处理流程**:
```
用户问题 
  → GraphQueryAgent (意图识别)
  → Schema检索
  → Gremlin生成
  → 执行查询
  → 结果解释
  → 返回答案
```

---

### 端点2: `/api/v1/direct-query` - 直接Gremlin查询 ⭐ 新增

**用途**: 专业人士直接执行Gremlin查询（适合开发者/DBA）

**请求**:
```json
POST /api/v1/direct-query
{
  "gremlin": "g.V().hasLabel('Person').has('city', '北京').limit(10)",
  "params": {}
}
```

**响应**:
```json
{
  "success": true,
  "data": [
    {"id": "1:张伟", "label": "Person", "properties": {...}},
    {"id": "2:李娜", "label": "Person", "properties": {...}}
  ],
  "count": 2
}
```

**安全特性**:
- ✅ 危险关键字过滤（drop, config, system等）
- ✅ 白名单验证（只允许安全前缀）
- ✅ 参数化查询支持
- ⚠️ 建议添加独立API密钥鉴权

**处理流程**:
```
Gremlin语句 
  → 安全检查
  → 参数替换
  → 执行查询
  → 返回原始数据
```

## 💻 开发指南

### 添加新的业务模块

假设要添加一个"报告生成"功能：

#### 步骤1: 创建服务类
```python
# services/reports/report_generator.py
from modules.database.client import get_db

class ReportGenerator:
    def __init__(self):
        self.db = get_db()
    
    def generate_person_report(self, city: str) -> dict:
        """生成某城市人员报告"""
        query = f"g.V().hasLabel('Person').has('city', '{city}').elementMap()"
        result = self.db.execute_gremlin(query)
        
        return {
            "city": city,
            "total_people": result.get("count", 0),
            "data": result.get("data", [])
        }
```

#### 步骤2: 添加API路由
```python
# app/api/v1/routes.py
from services.reports.report_generator import ReportGenerator

@api_bp.route('/report/person-by-city', methods=['POST'])
def generate_person_report():
    data = request.get_json()
    city = data.get('city')
    
    generator = ReportGenerator()
    report = generator.generate_person_report(city)
    
    return jsonify(report)
```

#### 步骤3: 测试
```bash
curl http://localhost:5000/api/v1/report/person-by-city \
  -X POST \
  -H "Content-Type: application/json" \
  -d "{\"city\": \"北京\"}"
```

### 扩展现有服务

#### 增强DirectQueryService的安全检查

```python
# services/queries/direct_query.py

class DirectQueryService:
    def _is_safe_query(self, query: str) -> tuple:
        """增强版安全检查"""
        query_lower = query.lower().strip()
        
        # 1. 危险关键字检查
        dangerous_keywords = ['drop', 'config', 'system', 'shutdown']
        for keyword in dangerous_keywords:
            if keyword in query_lower:
                return False, f"包含危险关键字: {keyword}"
        
        # 2. 白名单验证
        SAFE_PREFIXES = ['g.V()', 'g.E()', 'g.V().has(']
        if not any(query_lower.startswith(p) for p in SAFE_PREFIXES):
            return False, "查询必须以安全操作开头"
        
        # 3. 复杂度限制（防止超时）
        if query.count('.') > 20:  # 最多20步遍历
            return False, "查询过于复杂"
        
        return True, ""
```

## 🔐 安全最佳实践

### 1. 为直接查询添加API密钥

```python
# config.py
class Config:
    DIRECT_QUERY_API_KEY = os.getenv('DIRECT_QUERY_API_KEY', 'change_me')

# app/api/v1/routes.py
from config import Config

@api_bp.route('/direct-query', methods=['POST'])
def handle_direct_query():
    # 验证API密钥
    api_key = request.headers.get('X-API-KEY')
    if api_key != Config.DIRECT_QUERY_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    
    # ... 原有逻辑
```

### 2. 添加速率限制

```python
# app/__init__.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def create_app():
    app = Flask(__name__)
    
    # 初始化限流器
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # 对直接查询更严格的限制
    from app.api.v1.routes import api_bp
    limiter.limit("10/minute")(api_bp)
    
    return app
```

### 3. 输入验证

```python
# services/queries/direct_query.py

class DirectQueryRequest(BaseModel):
    gremlin: str = Field(..., max_length=2000)
    params: Optional[Dict] = None
    
    @validator('gremlin')
    def validate_gremlin(cls, v):
        # 禁止多行查询
        if '\n' in v:
            raise ValueError("不支持多行查询")
        
        # 禁止特殊字符
        if ';' in v:
            raise ValueError("不允许使用分号")
        
        return v
```

## 🧪 测试指南

### 单元测试

```python
# test_direct_query.py
import pytest
from unittest.mock import Mock
from services.queries.direct_query import DirectQueryService

def test_safe_query():
    """测试安全查询"""
    mock_db = Mock()
    service = DirectQueryService(mock_db)
    
    is_safe, reason = service._is_safe_query("g.V().limit(5)")
    assert is_safe == True

def test_unsafe_query():
    """测试不安全查询"""
    mock_db = Mock()
    service = DirectQueryService(mock_db)
    
    is_safe, reason = service._is_safe_query("g.V().drop()")
    assert is_safe == False
    assert "drop" in reason.lower()
```

运行测试：
```bash
pytest test_direct_query.py -v
```

### 集成测试

```python
# test_api_endpoints.py
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_natural_language_query(client):
    """测试自然语言查询端点"""
    response = client.post('/api/v1/query', json={
        "question": "找出所有人物"
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert "success" in data

def test_direct_query(client):
    """测试直接查询端点"""
    response = client.post('/api/v1/direct-query', json={
        "gremlin": "g.V().limit(1)"
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
```

## 📊 性能优化建议

### 1. 添加查询缓存

```python
# services/queries/direct_query.py
import redis
import json

class DirectQueryService:
    def __init__(self, db, cache_ttl=300):
        self.db = db
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.cache_ttl = cache_ttl
    
    def execute(self, query: str, params: dict = None) -> dict:
        # 生成缓存键
        cache_key = f"query:{hash(query)}"
        
        # 尝试从缓存获取
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # 执行查询
        result = self.db.execute_gremlin(query)
        
        # 存入缓存
        if result["success"]:
            self.redis.setex(cache_key, self.cache_ttl, json.dumps(result))
        
        return result
```

### 2. 异步查询（对于耗时操作）

```python
# 使用Celery进行异步处理
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def execute_heavy_query(gremlin: str):
    """异步执行重型查询"""
    db = get_db()
    return db.execute_gremlin(gremlin)

# API路由
@api_bp.route('/heavy-query', methods=['POST'])
def submit_heavy_query():
    task = execute_heavy_query.delay(request.json['gremlin'])
    return jsonify({"task_id": task.id})
```

## 🚀 部署清单

### 环境变量配置

```bash
# .env
# LLM配置
OPENAI_API_KEY=your_dashscope_key
OPENAI_MODEL=qwen-plus
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 数据库配置
HUGEGRAPH_HOST=localhost
HUGEGRAPH_PORT=8080
HUGEGRAPH_GRAPH=your_graph

# 安全配置
DIRECT_QUERY_API_KEY=your_secure_key_here
FLASK_SECRET_KEY=your_secret_key

# 可选：缓存
REDIS_URL=redis://localhost:6379/0
```

### 生产环境启动

```bash
# 使用Gunicorn
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Docker部署（可选）

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

## 📚 相关文档

- [ARCHITECTURE.md](ARCHITECTURE.md) - 详细架构说明
- [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) - 重构总结
- [scripts/README.md](scripts/README.md) - 测试数据生成器使用说明
- [modules/DATABASE_README.md](modules/DATABASE_README.md) - 数据库模块文档
- [modules/LLM_README.md](modules/LLM_README.md) - LLM模块文档

## ❓ 常见问题

### Q1: 旧代码还能用吗？
**A**: 是的！我们创建了向后兼容层，旧的导入路径仍然有效：
```python
# 旧方式（仍可用）
from modules.database import HugeGraphDB

# 新方式（推荐）
from modules.database.client import HugeGraphDB
```

### Q2: 如何迁移到新架构？
**A**: 逐步替换导入路径即可：
```python
# 1. 更新导入
from services.agents.agent import GraphQueryAgent  # 替代 langchain_agent

# 2. 运行测试确保正常
pytest test_*.py -v

# 3. 删除旧文件（确认无误后）
```

### Q3: 直接查询安全吗？
**A**: 已实现多层安全防护：
- 危险关键字过滤
- 白名单验证
- 建议添加API密钥和速率限制

### Q4: 如何添加新功能？
**A**: 遵循以下步骤：
1. 在`services/`下创建新模块
2. 实现业务逻辑
3. 在`app/api/v1/routes.py`添加路由
4. 编写测试

## 🎯 下一步行动

1. **立即执行**:
   - [ ] 运行 `python verify_refactoring.py` 验证
   - [ ] 启动服务 `python run.py`
   - [ ] 测试两个API端点

2. **短期改进**（1周内）:
   - [ ] 为直接查询添加API密钥
   - [ ] 添加速率限制
   - [ ] 完善错误处理

3. **中期规划**（1个月内）:
   - [ ] 添加Redis缓存
   - [ ] 集成LangSmith监控
   - [ ] 编写更多单元测试

4. **长期目标**（3个月内）:
   - [ ] Docker容器化
   - [ ] CI/CD流水线
   - [ ] 微服务拆分评估

---

**祝您使用愉快！** 🚀

如有问题，请查阅相关文档或提交Issue。
