# 开源图数据集导入指南

本指南介绍如何使用 `import_graph_dataset.py` 脚本向 HugeGraph 导入开源图数据集。

## 支持的数据集

### 1. MovieLens (推荐新手使用)
- **数据规模**: 约 600 用户, 9000 电影, 100000 评分
- **图结构**: 用户 -[RATED/TAGGED]-> 电影
- **适用场景**: 社交网络、推荐系统测试

### 2. Karate Club (空手道俱乐部)
- **数据规模**: 34 个成员, 78 条关系  
- **图结构**: 成员 -[KNOWS]-> 成员
- **适用场景**: 社区发现、图算法测试

### 3. DBLP (待完善)
- **数据规模**: 大型学术合作网络
- **图结构**: 作者 -[WRITES]-> 论文 -[PUBLISHED_IN]-> 会议, 论文 -[CITES]-> 论文
- **适用场景**: 知识图谱、学术网络分析

## 环境准备

### 1. 安装依赖
```bash
pip install pandas requests
```

### 2. 确保 HugeGraph 服务运行
确保您的 `.env` 文件中配置了正确的 HugeGraph 连接参数：
```bash
HUGEGRAPH_HOST=127.0.0.1
HUGEGRAPH_PORT=8080
HUGEGRAPH_GRAPH=hugegraph
```

## 使用方法

### 基本命令格式
```bash
python scripts/import_graph_dataset.py --dataset <数据集名称> [选项]
```

### 导入 MovieLens 数据集
```bash
# 导入完整的小型MovieLens数据集（约1000顶点）
python scripts/import_graph_dataset.py --dataset movielens

# 导入限制数量的MovieLens数据（更快的测试）
python scripts/import_graph_dataset.py --dataset movielens --max-vertices 500

# 清空现有数据后重新导入
python scripts/import_graph_dataset.py --dataset movielens --clear-first
```

### 导入 Karate Club 数据集
```bash
# 导入经典的Karate Club社交网络
python scripts/import_graph_dataset.py --dataset karate

# 清空后导入
python scripts/import_graph_dataset.py --dataset karate --clear-first
```

### 导入 DBLP 数据集
```bash
# DBLP功能待完善，当前版本仅创建Schema
python scripts/import_graph_dataset.py --dataset dblp
```

## 验证导入结果

导入完成后，可以使用以下方式验证数据：

### 1. 检查 Schema
```python
from modules.database.client import HugeGraphDB
db = HugeGraphDB()
print(db.get_schema_text())
```

### 2. 查询顶点和边数量
```python
# 顶点总数
result = db.execute_gremlin("g.V().count()")
print(f"顶点数: {result['data'][0]}")

# 边总数  
result = db.execute_gremlin("g.E().count()")
print(f"边数: {result['data'][0]}")
```

### 3. 查询具体数据（MovieLens示例）
```python
# 查询前5个用户
result = db.execute_gremlin("g.V().hasLabel('User').limit(5).elementMap()")

# 查询前5部电影
result = db.execute_gremlin("g.V().hasLabel('Movie').limit(5).elementMap()")

# 查询用户的评分关系
result = db.execute_gremlin("g.V().has('User', 'userId', 1).outE('RATED').inV().elementMap().limit(3)")
```

## 注意事项

1. **网络要求**: 脚本需要联网下载数据集，请确保网络连接正常
2. **内存要求**: 大型数据集导入可能需要较多内存，建议从小数据集开始测试
3. **清理操作**: `--clear-first` 参数会删除所有现有数据，请谨慎使用
4. **错误处理**: 如果导入过程中出现错误，脚本会继续尝试后续批次，不会完全中断
5. **性能优化**: 默认批量大小为1000，可根据您的HugeGraph服务器性能调整

## 故障排除

### 连接失败
- 检查 HugeGraph 服务是否正在运行
- 验证 `.env` 文件中的连接配置
- 确认防火墙没有阻止连接

### 导入缓慢
- 减少 `--max-vertices` 参数值
- 确保 HugeGraph 服务器有足够的内存和CPU资源
- 考虑在非高峰时段执行导入

### Schema 冲突
- 使用 `--clear-first` 参数清空现有Schema
- 或手动删除冲突的Schema元素后再导入