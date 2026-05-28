# 正式测试用例说明

## 📋 概述

本目录包含针对图数据库 Agent 系统的正式测试用例，共 30 个测试用例分为三个难度级别。

## 🎯 测试目标

1. **验证 Agent 查询能力**：测试 Agent 将自然语言转换为 Gremlin 查询的准确性
2. **建立基准答案**：使用标准 Gremlin 查询获取正确答案作为对比基准
3. **评估系统性能**：通过分层测试评估不同复杂度查询的处理效果

## 📊 测试用例分类

### 简单查询（Simple Queries）- 10条

**特点**：
- 单跳或无跳转查询
- 基本属性检索
- 简单计数操作
- 不涉及复杂聚合或过滤

**示例**：
```gremlin
// 统计电影总数
g.V().hasLabel('Movie').count()

// 查询用户评分的电影
g.V().has('User', 'userId', 1).out('rated').values('movieId')
```

### 中等查询（Medium Queries）- 10条

**特点**：
- 双跳关系查询
- 带条件过滤的聚合
- 简单的多条件组合
- 基础排序和去重

**示例**：
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

### 复杂查询（Complex Queries）- 10条

**特点**：
- 多跳关系路径
- 复杂聚合和分组
- 集合运算（交集、并集）
- 统计分析（标准差、方差）
- 推荐算法逻辑

**示例**：
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

## 🔧 使用方法

### 1. 生成基准答案

```bash
# 在项目根目录执行
python formal_test/generate_ground_truth.py
```

这将：
- 执行所有 30 个 Gremlin 查询
- 保存结果到 `ground_truth_answers.json`
- 显示执行统计信息

### 2. 运行 Agent 测试

```bash
# 测试 Agent 对相同问题的回答
python formal_test/test_agent_performance.py
```

### 3. 对比分析

```bash
# 比较 Agent 答案与基准答案
python formal_test/compare_results.py
```

## 📁 文件结构

```
formal_test/
├── README.md                      # 本说明文件
├── generate_ground_truth.py      # 生成基准答案脚本
├── test_cases.json               # 测试用例定义（可选）
├── ground_truth_answers.json     # 生成的基准答案（自动生成）
├── agent_results.json            # Agent 测试结果（自动生成）
└── comparison_report.json        # 对比分析报告（自动生成）
```

## 📈 评估指标

### 查询正确性
- **Gremlin 语法正确率**：Agent 生成的查询是否能成功执行
- **结果匹配度**：Agent 返回的数据是否与基准答案一致
- **语义准确性**：最终自然语言回答是否正确反映查询结果

### 性能指标
- **响应时间**：从问题提交到答案返回的时间
- **重试次数**：Agent 自我修正的次数
- **中间步骤数**：推理过程的复杂度

### 分级评估标准

| 级别 | 成功率要求 | 平均响应时间 | 说明 |
|------|-----------|-------------|------|
| 简单 | ≥ 90% | < 5秒 | 基本查询应高度准确 |
| 中等 | ≥ 75% | < 10秒 | 允许一定的推理错误 |
| 复杂 | ≥ 60% | < 20秒 | 复杂逻辑可能需多次修正 |

## ⚠️ 注意事项

1. **数据一致性**：确保测试前数据库已导入完整数据集
2. **时间戳处理**：部分查询涉及时间计算，需注意时区和格式
3. **浮点数精度**：评分相关的比较应考虑浮点误差
4. **空结果处理**：某些查询可能返回空结果，这是正常现象
5. **LLM 随机性**：Agent 的回答可能有变化，建议多次运行取平均值

## 🔍 测试用例详细列表

详见 `generate_ground_truth.py` 中的定义，包含：
- 问题描述
- 难度级别
- Gremlin 查询语句
- 预期结果类型
- 测试说明

## 📝 扩展建议

未来可以添加：
1. **边界情况测试**：空数据、异常输入等
2. **压力测试**：并发查询性能
3. **回归测试**：版本更新后的功能验证
4. **A/B 测试**：不同 Prompt 策略的效果对比
