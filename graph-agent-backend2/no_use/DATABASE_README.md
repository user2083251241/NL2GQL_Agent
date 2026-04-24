# modules/database.py 使用说明

## 功能概述

`HugeGraphDB` 类提供了完整的HugeGraph数据库操作接口：

### 1. 初始化（单例模式）
```python
from modules.database import HugeGraphDB

db = HugeGraphDB()  # 自动连接数据库
```

### 2. 执行Gremlin查询
```python
result = db.execute_gremlin("g.V().has('Person', 'name', '张三')")

# 返回格式：
{
    "success": True,
    "data": [...],  # 查询结果
    "count": 1      # 结果数量
}

# 失败时：
{
    "success": False,
    "data": [],
    "error": "错误信息"
}
```

### 3. 获取Schema信息
```python
schema = db.get_schema()

# 返回格式：
{
    "vertex_labels": ["Person", "Company"],
    "edge_labels": ["knows", "works_at"],
    "properties": {
        "Person": ["name", "age", "city"],
        "Company": ["name", "address"]
    }
}
```

### 4. 获取格式化Schema文本（用于Prompt）
```python
schema_text = db.get_schema_text()
# 返回可读的文本描述，可直接嵌入Prompt
```

### 5. 测试连接
```python
if db.test_connection():
    print("数据库连接正常")
```

## 便捷函数

```python
from modules.database import get_db

db = get_db()  # 获取数据库单例实例
```

## 测试

运行测试脚本验证功能：
```bash
python test_database.py
```
