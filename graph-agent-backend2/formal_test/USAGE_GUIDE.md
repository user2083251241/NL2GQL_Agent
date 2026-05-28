# 正式测试框架使用指南

## 📖 目录

1. [概述](#概述)
2. [快速开始](#快速开始)
3. [文件说明](#文件说明)
4. [使用方法](#使用方法)
5. [测试用例设计](#测试用例设计)
6. [常见问题](#常见问题)

---

## 概述

本测试框架为图数据库 Agent 系统提供了一套完整的自动化测试解决方案，包含：

- ✅ **30个标准化测试用例**（简单、中等、复杂三个级别）
- ✅ **基准答案生成工具**（使用标准 Gremlin 查询）
- ✅ **结果查看和分析工具**
- ✅ **详细的文档和示例**

### 核心价值

1. **可重复性**: 所有测试用例都有明确的预期结果
2. **可扩展性**: 易于添加新的测试用例
3. **可视化**: 提供多种查看和分析工具
4. **自动化**: 支持批量执行和结果对比

---

## 快速开始

### 1. 生成基准答案

```bash
# 在项目根目录执行
python formal_test/generate_ground_truth.py
```

这将：
- 连接 HugeGraph 数据库
- 执行所有 30 个 Gremlin 查询
- 保存结果到 `ground_truth_answers.json`

### 2. 查看测试结果

```bash
# 查看所有测试用例列表
python formal_test/view_answers.py --list

# 查看统计信息
python formal_test/view_answers.py --stats

# 查看特定测试用例
python formal_test/view_answers.py --id 1

# 按难度筛选
python formal_test/view_answers.py --level simple
```

### 3. 运行 Agent 测试（待实现）

```bash
# TODO: 创建 Agent 测试脚本
python formal_test/test_agent.py
```

---

## 文件说明

```
formal_test/
├── README.md                      # 测试用例详细说明
├── TEST_RESULTS_SUMMARY.md        # 测试执行结果总结
├── USAGE_GUIDE.md                 # 本使用指南
├── generate_ground_truth.py      # 基准答案生成脚本 ⭐
├── view_answers.py                # 答案查看工具 ⭐
├── ground_truth_answers.json     # 生成的基准答案（自动生成）
└── test_agent.py                  # Agent 测试脚本（待实现）
```

### 核心文件

#### `generate_ground_truth.py`
- **功能**: 执行所有测试用例的 Gremlin 查询并保存结果
- **输出**: `ground_truth_answers.json`
- **特点**: 
  - 自动处理数据库连接
  - 错误处理和重试机制
  - 详细的执行日志

#### `view_answers.py`
- **功能**: 交互式查看测试用例和结果
- **命令**:
  - `--list`: 列出所有测试用例
  - `--id N`: 查看第 N 个测试用例详情
  - `--level LEVEL`: 按难度筛选
  - `--stats`: 显示统计信息

#### `ground_truth_answers.json`
- **格式**: JSON 数组
- **结构**:
```json
{
  "id": 1,
  "question": "数据库中总共有多少部电影？",
  "level": "simple",
  "gremlin_query": "g.V().hasLabel('Movie').count()",
  "description": "统计 Movie 顶点总数",
  "execution_result": {
    "success": true,
    "data": [9742],
    "count": 1
  },
  "generated_at": "2026-05-20T17:08:43.459278"
}
```

---

## 使用方法

### 场景 1: 验证 Agent 查询准确性

```python
# 1. 加载基准答案
import json
with open('formal_test/ground_truth_answers.json') as f:
    ground_truth = json.load(f)

# 2. 对每个测试用例，调用 Agent
for test in ground_truth:
    agent_result = call_agent(test['question'])
    
    # 3. 比较结果
    expected_count = test['execution_result']['count']
    actual_count = len(agent_result['data'])
    
    if abs(expected_count - actual_count) < threshold:
        print(f"✅ 测试 #{test['id']} 通过")
    else:
        print(f"❌ 测试 #{test['id']} 失败")
```

### 场景 2: 性能基准测试

```python
import time

# 记录每个查询的执行时间
for test in ground_truth:
    start = time.time()
    result = call_agent(test['question'])
    elapsed = time.time() - start
    
    print(f"测试 #{test['id']}: {elapsed:.2f}秒")
```

### 场景 3: 回归测试

```bash
# 1. 保存当前基准答案
cp ground_truth_answers.json ground_truth_v1.json

# 2. 更新 Agent 代码后重新生成
python formal_test/generate_ground_truth.py

# 3. 比较差异
python -c "
import json
v1 = json.load(open('ground_truth_v1.json'))
v2 = json.load(open('ground_truth_answers.json'))
# 比较逻辑...
"
```

---

## 测试用例设计

### 简单查询（10条）

**特点**:
- 单跳或无跳转
- 基本属性检索
- 简单计数操作

**示例**:
```gremlin
// 统计电影总数
g.V().hasLabel('Movie').count()

// 查询用户评分的电影
g.V().has('User', 'userId', 1).out('rated').values('movieId')
```

**测试重点**:
- Gremlin 语法正确性
- 实体和关系识别准确性
- 基础过滤条件应用

### 中等查询（10条）

**特点**:
- 双跳关系查询
- 带条件过滤的聚合
- 简单的多条件组合

**示例**:
```gremlin
// 查找对特定电影评5分的用户
g.V().has('Movie', 'title', 'Toy Story (1995)')
  .inE('rated').has('rating', 5.0)
  .outV().values('userId')

// 计算某类型电影的平均评分
g.V().has('Genre', 'name', 'Action')
  .in('belongsTo').inE('rated')
  .values('rating').mean()
```

**测试重点**:
- 关系路径构建正确性
- 聚合函数应用
- 排序和限制操作

### 复杂查询（10条）

**特点**:
- 多跳关系路径
- 复杂聚合和分组
- 集合运算
- 统计分析

**示例**:
```gremlin
// 找出共同兴趣电影
g.V().has('User', 'userId', 1)
  .outE('rated').has('rating', gte(4.0)).inV()
  .aggregate('user1_movies')
  .V().has('User', 'userId', 2)
  .outE('rated').has('rating', gte(4.0)).inV()
  .where(within('user1_movies'))
  .values('title')
```

**测试重点**:
- 复杂逻辑推理能力
- 多步骤查询规划
- 自我修正机制

---

## 常见问题

### Q1: 为什么有些查询返回空结果？

**A**: 这是正常现象。可能的原因：
- 数据集中不存在符合条件的记录
- 过滤条件过于严格
- 时间范围不匹配

**解决方法**:
- 检查数据集是否完整
- 调整过滤条件
- 验证 Gremlin 查询逻辑

### Q2: 如何添加新的测试用例？

**A**: 
1. 在 `generate_ground_truth.py` 中添加新的测试用例定义
2. 编写对应的 Gremlin 查询
3. 运行脚本生成基准答案
4. 更新文档

```python
# 在 generate_simple_queries() 中添加
{
    "id": 31,
    "question": "你的新问题",
    "level": "simple",
    "gremlin_query": "g.V()...",
    "description": "问题描述"
}
```

### Q3: 如何处理 Groovy 语法兼容性问题？

**A**: 
- 某些高级 Gremlin 特性可能在 HugeGraph 中不支持
- 可以使用替代方案：
  ```python
  # 原始查询（可能不支持）
  .math('(_ / 2592000) % 12').intValue()
  
  # 替代方案
  # 在 Python 层面进行计算
  ```

### Q4: 测试失败时如何调试？

**A**:
1. 查看 `ground_truth_answers.json` 中的错误信息
2. 直接在 HugeGraph Studio 中执行 Gremlin 查询
3. 检查数据类型和格式
4. 简化查询逐步排查

### Q5: 如何评估 Agent 的表现？

**A**: 建议从以下维度评估：

| 维度 | 指标 | 目标值 |
|------|------|--------|
| 准确性 | Gremlin 语法正确率 | ≥ 90% |
| 完整性 | 结果匹配度 | ≥ 80% |
| 效率 | 平均响应时间 | < 10秒 |
| 稳定性 | 重试次数 | ≤ 2次 |

---

## 最佳实践

### 1. 定期更新基准答案

```bash
# 每月或数据集更新后
python formal_test/generate_ground_truth.py
```

### 2. 版本控制

```bash
# 保存历史版本
git add formal_test/ground_truth_answers.json
git commit -m "Update ground truth answers for v1.2"
```

### 3. 持续集成

```yaml
# .github/workflows/test.yml
name: Test Agent
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Tests
        run: python formal_test/test_agent.py
```

### 4. 文档维护

- 每次修改测试用例后更新文档
- 记录已知问题和解决方案
- 保持示例代码的最新性

---

## 下一步计划

- [ ] 实现 Agent 自动化测试脚本
- [ ] 添加结果对比分析工具
- [ ] 创建可视化报告生成器
- [ ] 集成到 CI/CD 流程
- [ ] 添加更多边界情况测试
- [ ] 性能基准测试框架

---

## 联系方式

如有问题或建议，请：
1. 查看项目 README.md
2. 提交 Issue
3. 联系开发团队

---

**最后更新**: 2026-05-20  
**版本**: 1.0.0  
**维护者**: Graph Agent Team
