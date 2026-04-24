"""
LangChain Agent 核心模块
实现图查询智能体的核心功能
"""
from .agent import GraphQueryAgent
from .tools import create_tools, ExecuteGremlinTool, GetSchemaTool
from .prompts import (
    create_text_to_gremlin_prompt,
    create_result_explanation_prompt,
    create_correction_prompt,
    get_system_prompt
)

"""
向后兼容模块 - 重定向到新的模块位置

警告：此模块已弃用，请使用以下新路径：
- from services.agents.agent import GraphQueryAgent
"""
from services.agents.agent import GraphQueryAgent

__all__ = [
    "GraphQueryAgent",
    "create_tools",
    "ExecuteGremlinTool",
    "GetSchemaTool",
    "create_text_to_gremlin_prompt",
    "create_result_explanation_prompt",
    "create_correction_prompt",
    "get_system_prompt"
]
