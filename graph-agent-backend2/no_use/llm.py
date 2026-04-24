"""
向后兼容模块 - 重定向到新的模块位置

警告：此模块已弃用，请使用以下新路径：
- from modules.llm.client import create_llm
- from modules.llm.client import get_llm
"""
from modules.llm.client import (
    create_llm,
    create_llm_with_retry,
    get_llm,
    reset_llm,
    ChatOpenAI
)

__all__ = ['create_llm', 'create_llm_with_retry', 'get_llm', 'reset_llm', 'ChatOpenAI']
