# Gremlin 执行准确率测试

## 功能说明

本目录包含用于验证 Agent 生成的 Gremlin 查询执行准确率的测试工具和结果。

### 主要功能

1. **端到端测试**: 通过 Agent 实例处理自然语言查询，提取生成的 Gremlin 语句并验证执行
2. **批量执行验证**: 自动执行所有 Gremlin 查询，验证其是否能成功运行
3. **计算通过率**: 统计执行成功率（成功执行的查询比例）
4. **生成详细报告**: 输出 JSON 和文本格式的详细测试报告

## 文件结构

```
accuracy_rate/
├── test_agent_gremlin_execution_sse.py   # Agent SSE 端到端测试脚本（推荐⭐）
├── test_agent_gremlin_execution.py       # Agent 直接调用测试脚本
├── test_gremlin_execution.py             # 直接 Gremlin 执行测试脚本
├── README.md                              # 本文档
├── QUICKSTART.md                          # 快速开始指南
├── .gitignore                             # Git 忽略配置
├── agent_gremlin_execution_results_simple_sse.json  # SSE测试结果（运行后生成）
├── agent_execution_summary_simple_sse.txt           # SSE测试摘要（运行后生成）
├── agent_gremlin_execution_results_simple.json      # 直接测试结果（运行后生成）
├── agent_execution_summary_simple.txt               # 直接测试摘要（运行后生成）
├── gremlin_execution_results.json         # 纯Gremlin测试结果（运行后生成）
└── execution_summary.txt                  # 纯Gremlin测试摘要（运行后生成）
```

## 测试脚本说明

### 1. Agent SSE 端到端测试（强烈推荐 ⭐）

**脚本**: `test_agent_gremlin_execution_sse.py`

**功能**: 
- 通过 HTTP POST 请求调用后端 SSE 流式接口 `/api/v1/graph-agent/query/stream`
- 解析 SSE 响应流，提取 `final_answer` 事件中的 JSON 数据
- 从 `"gremlin语句"` 字段提取 Agent 生成的 Gremlin 查询
- 执行提取的 Gremlin 查询，验证是否能成功执行
- 目前仅测试 simple 级别的查询

**优势**:
- ✅ 完全模拟真实前端调用场景
- ✅ 测试完整的 API 链路（HTTP → Agent → Database）
- ✅ 验证 SSE 流式通信的正确性
- ✅ 捕获推理过程中的所有步骤

**使用方法**:
```bash
# 1. 确保后端服务正在运行
python run.py

# 2. 在项目根目录执行测试
python formal_test/accuracy_rate/test_agent_gremlin_execution_sse.py
```

**输出文件**:
- `agent_gremlin_execution_results_simple_sse.json`: 完整的 JSON 格式测试结果
- `agent_execution_summary_simple_sse.txt`: 易读的文本格式摘要报告

### 2. Agent 直接调用测试

**脚本**: `test_agent_gremlin_execution.py`

**功能**: 
- 直接在代码中创建 `AgentQueryService` 实例
- 将自然语言问题输入给 Agent
- 从 Agent 返回的答案中提取 `"gremlin语句"` 字段
- 执行提取的 Gremlin 查询，验证是否能成功执行

**适用场景**:
- 快速调试 Agent 逻辑
- 不需要启动完整后端服务
- 单元测试场景

**使用方法**:
```bash
python formal_test/accuracy_rate/test_agent_gremlin_execution.py
```

**输出文件**:
- `agent_gremlin_execution_results_simple.json`: 完整的 JSON 格式测试结果
- `agent_execution_summary_simple.txt`: 易读的文本格式摘要报告

### 3. 直接 Gremlin 执行测试

**脚本**: `test_gremlin_execution.py`

**功能**:
- 直接从 ground_truth_answers.json 提取所有测试用例的 Gremlin 查询
- 批量执行这些查询，验证其是否能成功运行
- 不涉及 Agent，仅验证预定义的 Gremlin 语句

**适用场景**:
- 验证数据库连接是否正常
- 测试预定义 Gremlin 语句的正确性
- 作为 Agent 测试的基准对比

**使用方法**:
```bash
python formal_test/accuracy_rate/test_gremlin_execution.py
```

**输出文件**:
- `gremlin_execution_results.json`: 完整的 JSON 格式测试结果
- `execution_summary.txt`: 易读的文本格式摘要报告

## 前置条件

### 通用要求

1. 确保已生成 ground truth 数据：
   ```bash
   python formal_test/generate_ground_truth.py
   ```

2. 确保 HugeGraph 数据库正在运行且可访问

3. 确保 `.env` 配置文件中的数据库连接参数正确

### SSE 版本额外要求

4. 确保 LLM API 配置正确（用于 Agent 测试）

5. **必须启动后端服务**：
   ```bash
   python run.py
   ```
   
6. 确认后端服务监听地址为 `http://localhost:5000`（可在脚本中修改 `SSE_API_URL` 常量）

## 测试指标

### 执行通过率计算公式

```
执行通过率 = (成功执行的查询数 / 总查询数) × 100%
```

### 评级标准

- **100%**: 🎉 完美 - 所有 Gremlin 查询均能成功执行
- **≥80%**: ⚠️ 良好 - 大部分查询可以执行，但存在部分失败需要检查
- **<80%**: ❌ 需改进 - 大量查询执行失败，需要检查 Gremlin 语法或数据库配置

## 报告内容

### JSON 报告字段说明（SSE 版本）

```json
{
  "total": 10,                        // 测试总数
  "success_count": 9,                 // 执行成功数量
  "failed_count": 1,                  // 执行失败数量
  "extraction_failed_count": 0,       // Gremlin提取失败数量
  "api_call_failed_count": 0,         // API调用失败数量
  "execution_success_rate": 90.0,     // 执行通过率(%)
  "test_results": [                   // 详细测试结果
    {
      "id": 1,                        // 测试用例ID
      "question": "...",              // 自然语言问题
      "expected_gremlin": "...",      // 预期的 Gremlin 查询
      "api_success": true,            // API调用是否成功
      "final_answer": "...",          // final_answer 内容（部分）
      "extracted_gremlin": "...",     // 从 Agent 答案中提取的 Gremlin
      "extraction_success": true,     // 是否成功提取 Gremlin
      "execution_success": true,      // Gremlin 是否执行成功
      "execution_error": null,        // 执行错误信息（失败时）
      "result_count": 1               // 返回结果数量
    }
  ],
  "generated_at": "..."               // 测试时间
}
```

### 文本报告内容

1. **总体统计**
   - 测试时间、SSE 接口地址、总数、成功/失败数量、各类失败数量、通过率

2. **失败详情**
   - 区分 API 调用失败、提取失败、执行失败
   - 列出所有失败的查询及其错误信息
   - 包含预期 Gremlin 和实际提取的 Gremlin 对比
   - 如果提取失败，显示 final_answer 的原始内容

3. **成功列表**
   - 列出所有成功的查询及返回结果数量
   - 对比预期 Gremlin 和实际提取的 Gremlin

## 常见问题

### Q: SSE 版本和直接调用版本有什么区别？

A: 
- **SSE 版本**: 通过 HTTP 请求调用后端 API，完全模拟真实用户场景，测试整个系统链路
- **直接调用版本**: 在代码中直接创建 Agent 实例，绕过 HTTP 层，适合快速调试

### Q: 为什么有些查询会执行失败？

A: 可能的原因包括：
- Agent 生成的 Gremlin 语法错误
- 数据库中不存在对应的顶点/边标签
- 属性名称不匹配
- 查询逻辑错误（如使用了不存在的关系）
- HugeGraph 索引限制（某些属性没有索引，不能使用 has() 查询）

### Q: API 调用失败怎么办？

A: 
1. 确认后端服务正在运行：`python run.py`
2. 检查后端日志是否有错误
3. 确认 SSE 接口地址是否正确（默认 `http://localhost:5000/api/v1/graph-agent/query/stream`）
4. 检查网络连接和防火墙设置

### Q: 如何修复失败的查询？

A: 
1. 查看 `agent_execution_summary_simple_sse.txt` 中的错误信息
2. 分析是 Agent 生成错误还是执行环境错误
3. 如果是 Agent 生成问题，调整 Prompt 或工具定义
4. 如果是执行环境问题，检查数据库 Schema 和数据
5. 重新运行测试验证

### Q: 执行通过率低怎么办？

A: 
1. 检查数据库连接是否正常
2. 确认 Schema 是否正确加载
3. 验证测试数据是否已导入
4. 检查 Agent 的 Prompt 是否符合 HugeGraph 规范
5. 确认 LLM API 配置是否正确
6. 查看详细的错误日志定位问题

## 注意事项

1. **SSE 版本必须先启动后端服务**，否则会连接失败
2. Agent 测试需要调用 LLM API，可能产生费用
3. 某些复杂查询可能执行时间较长，请耐心等待（超时设置为 120 秒）
4. 测试不会影响数据库中的实际数据（仅执行查询操作）
5. 建议定期运行此测试，监控 Agent 的 Gremlin 生成能力和稳定性
6. 当前仅测试 simple 级别，后续可扩展到 medium 和 complex 级别
7. SSE 版本会记录所有推理步骤，便于调试和分析 Agent 行为
