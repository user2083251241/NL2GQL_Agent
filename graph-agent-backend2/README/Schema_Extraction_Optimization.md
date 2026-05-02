# Schema 提取优化方案

## 1. 问题背景

当前系统在每次查询时都会调用 `get_schema_info` 工具获取完整的数据库 Schema 信息，存在以下问题：

- **性能浪费**：同一个会话中的多次查询重复提取相同的 Schema
- **资源消耗**：频繁的 Schema 查询增加 HugeGraph 负载
- **响应延迟**：Schema 提取过程增加了每次查询的响应时间
- **LLM Token 浪费**：重复处理相同的 Schema 信息消耗 LLM token

## 2. 优化目标

- **会话级别缓存**：每个会话只在首次需要时提取完整 Schema
- **智能复用**：后续查询直接使用缓存的 Schema 信息
- **自动失效**：支持缓存过期和手动清理机制
- **无缝集成**：保持现有 API 接口不变，对用户透明

## 3. 技术方案

### 3.1 架构设计

```
用户请求 → AgentService → GraphAgent → [缓存策略] → 工具调用
                                    ↓
                    get_cached_schema (优先) → 缓存命中？
                                    ↓ 是              ↓ 否
                            直接使用缓存Schema    get_schema_info + cache_current_schema
```

### 3.2 核心组件

#### SchemaCache (会话级缓存)
- **存储结构**：`{session_id: schema_data}`
- **缓存策略**：TTL 过期（默认 1 小时）
- **线程安全**：支持多用户并发访问
- **内存管理**：自动清理过期缓存

#### 新增工具
1. **get_cached_schema**：获取缓存的 Schema 信息
2. **cache_current_schema**：缓存当前 Schema 信息

#### 现有工具保留
- **get_schema_info**：获取最新 Schema（缓存未命中时使用）
- **execute_gremlin**：执行 Gremlin 查询

### 3.3 工作流程

#### 首次查询（缓存未命中）
1. Agent 调用 `get_cached_schema` → 返回 "缓存未命中"
2. Agent 调用 `get_schema_info` → 获取完整 Schema
3. Agent 调用 `cache_current_schema` → 缓存 Schema 到当前会话
4. Agent 调用 `execute_gremlin` → 执行查询并返回结果

#### 后续查询（缓存命中）
1. Agent 调用 `get_cached_schema` → 返回缓存的 Schema
2. Agent 直接使用缓存 Schema 生成 Gremlin 查询
3. Agent 调用 `execute_gremlin` → 执行查询并返回结果

## 4. 实现细节

### 4.1 SchemaCache 类实现

```python
# modules/memory/schema_cache.py
class SchemaCache:
    def __init__(self, cache_ttl: int = 3600):
        self.cache_ttl = cache_ttl
        self._schema_cache: Dict[str, dict] = {}
        self._last_access: Dict[str, float] = {}
    
    def get_schema(self, session_id: str) -> Optional[dict]:
        """获取会话的Schema缓存，自动处理过期"""
        # ... 实现逻辑 ...
    
    def set_schema(self, session_id: str, schema_data: dict):
        """设置会话的Schema缓存"""
        # ... 实现逻辑 ...
    
    def clear_session_cache(self, session_id: str):
        """清理指定会话的缓存"""
        # ... 实现逻辑 ...
```

### 4.2 新增工具实现

```python
# services/agents/tools.py
class GetCachedSchemaTool(BaseTool):
    name = "get_cached_schema"
    description = "获取当前会话缓存的数据库Schema信息..."

class CacheSchemaTool(BaseTool):
    name = "cache_current_schema" 
    description = "将当前获取到的Schema信息缓存到当前会话中..."
```

### 4.3 系统提示词更新

```python
# services/agents/prompts.py
SYSTEM_PROMPT = """
...
工作流程建议：
1. 首先调用get_cached_schema获取缓存的Schema
2. 如果缓存存在，直接使用缓存的Schema生成查询  
3. 如果缓存未命中，调用get_schema_info获取最新Schema
4. 获取到新Schema后，立即调用cache_current_schema进行缓存
5. 基于Schema信息生成并执行Gremlin查询
"""
```

### 4.4 Agent 初始化调整

```python
# services/agents/agent2.py
class GraphAgent:
    def __init__(self, llm, db, schema_cache=None, session_id=None):
        self.schema_cache = schema_cache
        self.session_id = session_id
        # 动态创建工具列表，包含缓存工具（如果有）
```

## 5. 集成步骤

### 5.1 第一阶段：基础缓存实现
1. 创建 `SchemaCache` 类
2. 实现 `GetCachedSchemaTool` 和 `CacheSchemaTool`
3. 更新系统提示词
4. 修改 `GraphAgent` 支持动态工具创建

### 5.2 第二阶段：服务层集成
1. 在 `AgentQueryService` 中初始化 `SchemaCache`
2. 修改 `query` 方法传递 `schema_cache` 和 `session_id`
3. 更新 API 路由确保 `session_id` 正确传递

### 5.3 第三阶段：测试验证
1. 编写单元测试验证缓存功能
2. 进行性能测试对比优化前后效果
3. 验证多用户并发场景下的正确性

## 6. 性能预期

### 6.1 性能收益
| 指标 | 优化前 | 优化后 | 提升幅度 |
|------|--------|--------|----------|
| Schema 提取次数 | N次/会话 | 1次/会话 | 减少 (N-1)/N |
| 平均响应时间 | T ms | T - Δt ms | 提升 Δt/T% |
| HugeGraph 负载 | 高 | 低 | 显著降低 |
| LLM Token 消耗 | 高 | 低 | 显著降低 |

### 6.2 资源消耗
- **内存占用**：每个会话约 1-5KB Schema 数据
- **缓存容量**：支持数千个并发会话
- **清理策略**：1小时 TTL 自动清理

## 7. 安全与可靠性

### 7.1 数据一致性
- **缓存失效**：TTL 机制确保 Schema 不会长期过期
- **手动刷新**：提供 API 接口支持强制刷新缓存
- **降级策略**：缓存失效时自动回退到实时 Schema 提取

### 7.2 错误处理
- **缓存异常**：不影响主查询流程，自动降级
- **内存溢出**：限制最大缓存数量，LRU 淘汰策略
- **并发安全**：线程安全的缓存操作

## 8. 扩展考虑

### 8.1 高级功能（可选）
1. **Schema 版本检测**：监控 HugeGraph Schema 变更，自动失效缓存
2. **分层缓存**：会话缓存 + 全局缓存（适用于稳定 Schema）
3. **预热机制**：服务启动时预加载常用 Schema
4. **统计监控**：记录缓存命中率、节省的查询次数等指标

### 8.2 与现有架构兼容
- **向后兼容**：不传递 `session_id` 的请求仍可正常工作
- **渐进式部署**：可以逐步启用缓存功能
- **配置化**：缓存 TTL、最大容量等参数可配置

## 9. 测试方案

### 9.1 功能测试
- 验证首次查询正确提取并缓存 Schema
- 验证后续查询正确使用缓存 Schema
- 验证缓存过期后自动重新提取 Schema
- 验证多用户会话间的缓存隔离

### 9.2 性能测试
- 对比优化前后的平均响应时间
- 测试高并发场景下的缓存性能
- 验证内存使用情况和清理机制

### 9.3 回归测试
- 确保现有功能不受影响
- 验证错误处理和降级机制
- 测试边界条件和异常场景

## 10. 部署与维护

### 10.1 部署步骤
1. 部署新代码到测试环境
2. 进行完整的功能和性能测试
3. 监控缓存命中率和系统性能
4. 逐步上线到生产环境

### 10.2 监控指标
- 缓存命中率
- Schema 提取频率
- 内存使用情况
- 查询响应时间分布

### 10.3 维护任务
- 定期分析缓存效果和性能数据
- 根据实际使用情况调整缓存参数
- 监控和处理缓存相关的异常情况

---

> **实施建议**：此优化方案应作为独立的功能模块开发，确保与现有代码的解耦。建议先在测试环境中充分验证后再部署到生产环境。