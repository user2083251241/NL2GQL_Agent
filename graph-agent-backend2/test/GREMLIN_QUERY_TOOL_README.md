# Gremlin 交互式查询工具使用说明

## 📖 简介

这是一个命令行交互式的 Gremlin 查询工具，让你可以直接输入 Gremlin 语句并立即查看执行结果。

## 🚀 快速开始

### 启动工具
```bash
python test/test_gremlin_query.py
```

### 基本用法
```
gremlin> g.V().limit(5)
```

## 💡 内置命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `help` | 显示帮助信息 | `gremlin> help` |
| `schema` | 查看数据库 Schema | `gremlin> schema` |
| `history` | 查看查询历史 | `gremlin> history` |
| `clear` | 清屏 | `gremlin> clear` |
| `export N` | 导出第 N 条历史记录 | `gremlin> export 1` |
| `exit/quit` | 退出程序 | `gremlin> exit` |

## 📝 查询示例

### 1. 基础查询
```gremlin
# 查询前10个顶点
g.V().limit(10)

# 查询所有User类型的顶点
g.V().hasLabel('User')

# 统计User数量
g.V().hasLabel('User').count()
```

### 2. 属性过滤
```gremlin
# 按属性值查询
g.V().has('Movie', 'title', 'Toy Story (1995)')

# 查询特定用户
g.V().has('User', 'userId', 1)
```

### 3. 边查询
```gremlin
# 查询前5条rated边
g.E().hasLabel('rated').limit(5)

# 查询某用户的评分记录
g.V().has('User', 'userId', 1).outE('rated')
```

### 4. 遍历查询
```gremlin
# 用户评分过的电影
g.V().has('User', 'userId', 1).outE('rated').inV().values('title')

# 电影的类型
g.V().has('Movie', 'title', 'Toy Story (1995)').out('belongsTo').values('name')
```

### 5. 聚合查询
```gremlin
# 动作电影的平均评分
g.V().has('Genre', 'name', 'Action').in('belongsTo').inE('rated').values('rating').mean()

# 每部电影的评分数量
g.V().hasLabel('Movie').project('title', 'count').by(values('title')).by(inE('rated').count()).limit(5)
```

## 🔧 高级功能

### 多行输入
对于复杂的查询，可以使用分号 `;` 进行多行输入：
```
gremlin> g.V().has('User', 'userId', 1);
       ... .outE('rated');
       ... .inV();
       ... .values('title');
```

### 查询历史
- 自动保存最近 50 条查询记录
- 使用 `history` 命令查看
- 使用 `export N` 导出指定记录为 JSON 文件

### 结果展示
- ✅ 成功查询：显示结果数量和详细数据
- ❌ 失败查询：显示错误信息
- 结果超过 10 条时，只显示前 10 条并提示总数

## ⚠️ 注意事项

1. **性能考虑**：避免执行无限制的全量查询（如 `g.V()`），建议始终添加 `.limit()`
2. **超时控制**：查询有默认超时时间，复杂查询可能超时
3. **数据安全**：禁止执行危险操作（如 `drop()`、`config()` 等）
4. **连接管理**：工具使用单例模式的数据库连接，无需手动管理

## 🎯 使用场景

- 🔍 快速验证 Gremlin 查询语法
- 📊 探索数据库结构和内容
- 🧪 测试复杂查询的逻辑正确性
- 📈 分析查询性能和结果格式
- 💾 导出查询结果用于进一步分析

## 📄 输出文件

导出的 JSON 文件包含：
- 原始查询语句
- 执行结果数据
- 执行时间戳
- 成功/失败状态

文件保存在 `test/` 目录下，命名格式：`gremlin_query_YYYYMMDD_HHMMSS.json`
