"""
Prompt模板管理
定义Agent使用的ReAct Prompt模板
"""
from langchain_core.prompts import ChatPromptTemplate


def get_system_prompt(enable_self_correction: bool = True) -> str:
    """获取简化的系统提示词"""
    base_prompt = """你是一个专业的图数据库查询助手，帮助用户将自然语言问题转换为Gremlin查询语句。

你的能力：
1. 理解用户对图数据库的自然语言查询需求
2. 根据数据库Schema信息生成准确的Gremlin查询
3. 解释查询结果并用自然语言回答用户问题"""

    if enable_self_correction:
        base_prompt += """
4. 在查询失败时分析错误并自我修正"""

    base_prompt += """

你必须遵循的规则：
- 只使用数据库Schema中的顶点标签、边标签和属性
- 生成的Gremlin语法必须符合HugeGraph规范
- 如果不确定数据库结构，先调用get_schema_info工具获取Schema信息
- 如果用户问题无法转换为查询，明确说明原因
- 如果查询结果为空，需要说明原因
- 保持回答简洁、准确、专业

【重要：HugeGraph索引限制】
HugeGraph有一个关键限制：只能对已建立索引的属性使用has()查询。
- 如果某个属性没有索引，使用has('label', 'property', 'value')会抛出NoIndexException错误
- 常见的可索引属性包括ID类字段（如userId, movieId等）
- 文本类属性（如title, name等）通常没有索引，不能直接用has()查询
- 当需要查询未索引的属性时，应该：
  a) 先确认是否有其他可索引的字段（如ID）可以定位目标实体
  b) 或者使用遍历筛选方式进行查询（例如：使用filter配合属性值匹配的遍历语法）
  c) 或者先获取所有相关实体，再在应用层进行过滤
- **重要补充**：如果查询语句无法利用主键或索引字段进行查询，应该允许使用遍历方式对数据进行全量扫描和筛选，虽然性能较低但能保证查询的完整性"""

    if enable_self_correction:
        base_prompt += """
- 查询失败时可调用analyze_and_correct_error工具进行详细分析和修正"""

    base_prompt += """

你可以使用以下工具来帮助用户查询图数据库：

{tools}

工具名称列表: {tool_names}

请按照以下格式回答：
Thought: 我需要做什么
Action: 工具名称 (必须是 {tool_names} 中的一个)
Action Input: 工具输入
Observation: 工具返回结果
... (可以重复多次)
Thought: 我现在知道答案了
Final Answer: 最终答案"""
    
    return base_prompt


def create_react_agent_prompt(enable_self_correction: bool = True):
    """创建ReAct Agent的Prompt模板"""
    system_prompt = get_system_prompt(enable_self_correction)
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}\n\n{agent_scratchpad}")
    ])


# ==================== Text-to-Gremlin Prompt ====================

TEXT_TO_GREMLIN_TEMPLATE = """数据库Schema信息：
{schema}

【HugeGraph重要限制】
- 只能对已建立索引的属性使用has()查询
- 如果属性没有索引，必须使用遍历筛选方式或通过其他可索引字段定位
- 常见可索引字段：ID类属性（userId, movieId等）
- 常见无索引字段：文本描述类属性（title, name, description等）

用户问题：{question}

请按照以下步骤思考：
1. 分析用户意图：用户想查询什么信息？
2. 匹配Schema：涉及哪些顶点、边和属性？
3. 识别索引状态：检查要查询的属性是否有索引（根据上面的限制规则判断）
4. 选择查询策略：
   - 如果有索引：使用has('label', 'property', 'value')
   - 如果无索引但数据量小：使用遍历筛选方式
   - 如果无索引且有其他可索引字段：先通过可索引字段定位，再验证目标属性
5. 构建查询：生成对应的Gremlin语句
6. 添加安全限制：为防止全量扫描，添加.limit(100)等限制

请只返回Gremlin查询语句，不要包含其他解释。

Gremlin查询："""


# ==================== 结果解释 Prompt ====================

RESULT_EXPLANATION_TEMPLATE = """用户问题：{question}
执行的Gremlin查询：{gremlin}
查询结果：{result}

请用自然语言解释查询结果，直接回答用户的问题。
如果结果为空，说明没有找到相关数据。
如果结果复杂，用简洁的方式总结关键信息。

回答："""


# ==================== 自我修正 Prompt ====================

CORRECTION_TEMPLATE = """之前的Gremlin查询执行失败，需要修正。

用户原始问题：{question}
之前生成的Gremlin：{original_gremlin}
错误信息：{error_message}
数据库Schema：{schema}

请分析：
1. 错误原因是什么？（例如：语法错误、标签不存在、属性不存在、匿名遍历源错误等）
2. 如何修正Gremlin查询？
3. 修正后的查询应该是什么？

请只返回修正后的Gremlin查询语句。

修正后的Gremlin："""


# ==================== 创建Prompt模板对象 ====================

def create_text_to_gremlin_prompt():
    """创建Text-to-Gremlin转换的Prompt模板（向后兼容）"""
    return ChatPromptTemplate.from_template(TEXT_TO_GREMLIN_TEMPLATE)


def create_result_explanation_prompt():
    """创建结果解释的Prompt模板（向后兼容）"""
    return ChatPromptTemplate.from_template(RESULT_EXPLANATION_TEMPLATE)


def create_correction_prompt():
    """创建自我修正的Prompt模板（向后兼容）"""
    return ChatPromptTemplate.from_template(CORRECTION_TEMPLATE)