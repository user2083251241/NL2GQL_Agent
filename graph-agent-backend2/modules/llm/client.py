"""
LLM模块 - LangChain语言模型工厂
负责创建和配置ChatModel实例
"""
from langchain_openai import ChatOpenAI
from config import Config
from typing import Optional


def create_llm(
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    verbose: bool = None
) -> ChatOpenAI:
    """
    创建LangChain ChatOpenAI实例
    
    Args:
        model: 使用的模型名称，默认从配置读取
        temperature: 温度参数（0-1），控制随机性
        max_tokens: 最大生成token数
        verbose: 是否输出详细日志，默认从配置读取
        
    Returns:
        ChatOpenAI实例
    """
    # 使用配置中的默认值
    if model is None:
        model = Config.OPENAI_MODEL
    
    if verbose is None:
        verbose = Config.LANGCHAIN_VERBOSE
    
    # 验证API密钥
    if not Config.OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY 未配置！\n"
            "请在 .env 文件中设置 OPENAI_API_KEY=your_api_key"
        )
    
    # 构建初始化参数
    kwargs = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "openai_api_key": Config.OPENAI_API_KEY,
        "verbose": verbose
    }
    
    # 如果配置了自定义API地址，添加到参数中
    if Config.OPENAI_BASE_URL:
        kwargs["openai_api_base"] = Config.OPENAI_BASE_URL
        #print(f"🔧 使用自定义API地址: {Config.OPENAI_BASE_URL}")
    
    # 创建并返回ChatOpenAI实例
    llm = ChatOpenAI(**kwargs)
    
    #print(f"✅ LLM初始化成功: {model} (temperature={temperature})")
    return llm


def create_llm_with_retry(
    max_retries: int = 3,
    **kwargs
) -> ChatOpenAI:
    """
    创建带重试机制的LLM实例
    
    Args:
        max_retries: 最大重试次数
        **kwargs: 传递给 create_llm 的参数
        
    Returns:
        ChatOpenAI实例
    """
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        try:
            #print(f"🔄 尝试初始化LLM (第{attempt}次)...")
            llm = create_llm(**kwargs)
            
            # 测试连接
            test_response = llm.invoke("Hello")
            print(f"✅ LLM连接测试成功")
            
            return llm
            
        except Exception as e:
            last_error = e
            print(f"⚠️ LLM初始化失败 (第{attempt}次): {e}")
            
            if attempt < max_retries:
                import time
                wait_time = 2 ** attempt  # 指数退避
                print(f"   等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
    
    # 所有重试都失败
    raise Exception(f"LLM初始化失败，已重试{max_retries}次。最后错误: {last_error}")


# 便捷函数：获取全局LLM实例（单例）
_global_llm = None


def get_llm(**kwargs) -> ChatOpenAI:
    """
    获取全局LLM单例实例
    
    Args:
        **kwargs: 传递给 create_llm 的参数
        
    Returns:
        ChatOpenAI实例（单例）
    """
    global _global_llm
    
    if _global_llm is None:
        _global_llm = create_llm(**kwargs)
    
    return _global_llm


def reset_llm():
    """重置全局LLM实例（用于测试或重新配置）"""
    global _global_llm
    _global_llm = None
    print("🔄 LLM实例已重置")
