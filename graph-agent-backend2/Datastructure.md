# 1.agent_result——agent查询结果，是一个字典
   {
    "output": "最终的自然语言答案",
    "intermediate_steps": [
        # 中间执行步骤列表
    ],
    # 其他可能的元数据字段
   }
1️⃣ output 字段
类型: 字符串
内容: LLM 生成的最终答案（Final Answer）
示例: "Person_0 在 Company_13 公司工作。"
特点:
是 ReAct 流程的终点
通常以 "Final Answer:" 开头（取决于 Prompt 模板）
2️⃣ intermediate_steps 字段
类型: 元组列表 [(AgentAction, observation), ...]
作用: 记录 Agent 的完整思考和执行过程
每个步骤包含:
AgentAction 对象：
{
    "tool": "execute_gremlin",  # 使用的工具名称
    "tool_input": {
        "gremlin_query": "g.V().has('Person', 'name', 'Person_0').out('works_at').values('name')"
    },
    "log": "Thought: 我需要找到Person_0所在公司...\nAction: execute_gremlin...",
    "type": "AgentAction"
}
observation (观察结果)
类型: 可能是字符串或字典（问题根源！）
内容: 工具执行后的返回结果
 字符串示例:
 "✅ 查询成功
   结果数量: 1
   数据: ['Company_13']"

字典示例 (理想情况)：
{
    "success": True,
    "data": ["Company_13"],
    "count": 1
}