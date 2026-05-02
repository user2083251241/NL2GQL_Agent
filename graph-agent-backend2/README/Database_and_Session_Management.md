# 数据库存储和会话管理实现指南

## 1. 设计原则

### 1.1 项目定位
- **公共查询服务**：所有用户共享同一份数据，无需用户数据隔离
- **无需身份认证**：不实现用户注册、登录、权限管理等复杂功能
- **极致精简**：只保留必要的用户管理功能，用于个性化记忆和使用统计

### 1.2 核心目标
- 支持短期记忆（对话上下文）
- 实现长期记忆（可选，用于个性化）
- 提供使用统计和偏好设置
- 保持零门槛用户体验

## 2. MySQL数据库表结构设计

### 2.1 users表（核心用户信息）

```sql
CREATE TABLE users (
    user_id VARCHAR(36) PRIMARY KEY,        -- UUID字符串，避免暴露用户数量
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 基础信息（可选）
    username VARCHAR(50) UNIQUE,             -- 用户名，可用于识别
    
    -- 使用统计
    total_queries INT DEFAULT 0,            -- 总查询次数
    last_active_at TIMESTAMP NULL           -- 最后活跃时间
);
```

### 2.2 user_preferences表（用户偏好设置）

```sql
CREATE TABLE user_preferences (
    user_id VARCHAR(36) PRIMARY KEY,
    preferences JSON,                       -- 存储用户偏好设置
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

### 2.3 user_sessions表（会话管理）

```sql
CREATE TABLE user_sessions (
    session_id VARCHAR(64) PRIMARY KEY,     -- 会话ID（UUID或哈希值）
    user_id VARCHAR(36),                    -- 关联用户（可为空，支持游客）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,                   -- 会话过期时间
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

### 2.4 禁止项
- ❌ 不存储密码、邮箱、手机号等个人敏感信息
- ❌ 不实现复杂的权限角色表
- ❌ 不收集非必要的个人信息

## 3. 会话管理机制

### 3.1 无认证场景下的会话识别

#### 前端职责
- **生成Session ID**：首次访问时生成唯一标识符（UUID）
- **维护Session ID**：通过localStorage持久化存储
- **传递Session ID**：每次API请求都包含该参数

```javascript
// 前端Session ID管理示例
function getSessionId() {
    let sessionId = localStorage.getItem('graph_agent_session_id');
    if (!sessionId) {
        sessionId = generateUUID(); // 生成UUID
        localStorage.setItem('graph_agent_session_id', sessionId);
    }
    return sessionId;
}

// API请求示例
const queryData = {
    query: "用户的问题",
    session_id: getSessionId(),  // 关键：传递会话ID
    timestamp: Date.now()
};
```

#### 后端职责
- **接收Session ID**：作为可选参数处理
- **存储会话历史**：基于Session ID维护短期记忆
- **自动清理**：支持基于时间的过期机制

### 3.2 现有系统集成

#### API接口支持
当前系统已在 `/api/graph-agent/query` 接口中支持 `session_id` 参数：

```json
{
    "query": "用户输入的自然语言问题",
    "session_id": "会话ID（可选）",
    "timestamp": 1234567890
}
```

#### 短期记忆实现
- **内存缓存**：使用Python字典存储 `{session_id: deque}` 结构
- **自动截断**：基于token数量限制防止OOM
- **会话隔离**：每个session_id独立维护对话历史

### 3.3 会话生命周期

| 阶段 | 行为 | 说明 |
|------|------|------|
| **创建** | 前端生成UUID | 首次访问时自动创建 |
| **使用** | 每次查询携带相同ID | 维护对话上下文 |
| **过期** | 后端自动清理 | 默认1小时无活动后过期 |
| **清除** | 提供手动清理接口 | 用户可主动清除历史 |

## 4. 扩展到长期记忆（可选）

### 4.1 向量数据库集成
- **Chroma**：轻量级向量数据库，适合初期开发
- **嵌入模型**：使用text-embedding-ada-002或开源bge-small
- **记忆写入**：在Agent完成有效交互后触发记忆存储
- **记忆检索**：每次新对话开始时检索相关历史

### 4.2 表结构扩展
```sql
-- 长期记忆表（可选）
CREATE TABLE long_term_memories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36),
    content TEXT,                           -- 记忆内容摘要
    embedding VECTOR,                       -- 向量表示（如果MySQL支持）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

## 5. 实施步骤

### 5.1 阶段1：基础会话管理
1. 创建MySQL数据库和表结构
2. 集成短期记忆模块到现有Agent
3. 更新前端实现Session ID管理
4. 测试多轮对话上下文保持

### 5.2 阶段2：用户统计和偏好
1. 实现users表的自动创建（首次使用时）
2. 添加偏好设置功能
3. 实现使用统计埋点
4. 提供数据清理和导出功能

### 5.3 阶段3：长期记忆（可选）
1. 集成向量数据库（Chroma）
2. 实现记忆摘要和向量化
3. 添加记忆检索和注入逻辑
4. 优化成本控制和隐私保护

## 6. 安全和隐私考虑

### 6.1 数据安全
- **自动过期**：会话数据默认1小时过期
- **匿名化**：不收集可识别个人信息
- **加密存储**：敏感数据应加密存储（如需要）

### 6.2 隐私保护
- **用户控制**：提供清除会话历史的接口
- **透明度**：明确告知用户数据使用方式
- **合规性**：遵循GDPR等隐私法规要求

## 7. 性能优化建议

### 7.1 缓存策略
- **短期记忆**：内存缓存 + 自动清理
- **Schema信息**：MySQL缓存高频访问的元数据
- **查询结果**：对高频查询实施TTL缓存

### 7.2 数据库优化
- **索引优化**：为session_id、user_id、expires_at添加索引
- **连接池**：使用mysql.connector.pooling管理连接
- **批量操作**：减少频繁的小事务操作

## 8. 监控和维护

### 8.1 监控指标
- 会话创建/过期数量
- 内存使用情况
- 查询成功率和响应时间
- 用户活跃度统计

### 8.2 维护任务
- 定期清理过期会话数据
- 监控数据库性能和容量
- 备份重要用户数据（如偏好设置）
- 审计数据访问日志

---

> **注意**：本方案严格遵循项目的公共查询服务定位，避免过度工程化。所有功能都以最小可行产品（MVP）为原则，确保快速验证和迭代。