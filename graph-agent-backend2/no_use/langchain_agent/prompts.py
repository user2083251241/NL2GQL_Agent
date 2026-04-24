"""
Prompt模板管理
定义Agent使用的各种Prompt模板
"""
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate


# ==================== 系统提示词 ====================

SYSTEM_PROMPT = """你是一个专业的图数据库查询助手，专门帮助用户将自然语言问题转换为Gremlin查询语句。

你的核心能力：
1. 理解用户对图数据库的自然语言查询需求
2. 根据提供的Schema信息生成准确的Gremlin查询
3. 解释查询结果并用自然语言回答用户问题
4. 在查询失败时分析错误并自我修正

你必须遵循的规则：
- 只使用提供的Schema中的顶点标签、边标签和属性
- 生成的Gremlin语法必须符合HugeGraph规范
- 如果用户问题无法转换为查询，明确说明原因
- 保持回答简洁、准确、专业"""


# ==================== Text-to-Gremlin Prompt ====================

TEXT_TO_GREMLIN_TEMPLATE = """数据库Schema信息：
{schema}

用户问题：{question}

请按照以下步骤思考：
1. 分析用户意图：用户想查询什么信息？
2. 匹配Schema：涉及哪些顶点、边和属性？
3. 构建查询：生成对应的Gremlin语句
4. 验证语法：确保Gremlin语法正确

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
1. 错误原因是什么？
2. 如何修正Gremlin查询？
3. 修正后的查询应该是什么？

请只返回修正后的Gremlin查询语句。

修正后的Gremlin："""


# ==================== 创建Prompt模板对象 ====================

def create_text_to_gremlin_prompt():
    """创建Text-to-Gremlin转换的Prompt模板"""
    return ChatPromptTemplate.from_template(TEXT_TO_GREMLIN_TEMPLATE)


def create_result_explanation_prompt():
    """创建结果解释的Prompt模板"""
    return ChatPromptTemplate.from_template(RESULT_EXPLANATION_TEMPLATE)


def create_correction_prompt():
    """创建自我修正的Prompt模板"""
    return ChatPromptTemplate.from_template(CORRECTION_TEMPLATE)


def get_system_prompt():
    """获取系统提示词"""
    return SYSTEM_PROMPT
