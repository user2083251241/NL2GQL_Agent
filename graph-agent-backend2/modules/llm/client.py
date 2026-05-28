"""
LLM模块 - LangChain语言模型工厂
负责创建和配置ChatModel实例
"""
from langchain_openai import ChatOpenAI
from config import Config
from typing import Optional
from langchain_core.callbacks import BaseCallbackHandler


class TokenUsageCallbackHandler(BaseCallbackHandler):
    """
    Token使用统计回调处理器
    
    用于捕获LLM调用过程中的token消耗信息
    """
    
    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.calls_count = 0
        
    def on_llm_end(self, response, **kwargs) -> None:
        """当LLM生成结束时触发，提取token使用信息"""
        try:
            # LangChain的LLM响应中包含token使用信息
            if hasattr(response, 'llm_output') and response.llm_output:
                token_usage = response.llm_output.get('token_usage', {})
                
                if token_usage:
                    prompt_tokens = token_usage.get('prompt_tokens', 0)
                    completion_tokens = token_usage.get('completion_tokens', 0)
                    total_tokens = token_usage.get('total_tokens', 0)
                    
                    self.prompt_tokens += prompt_tokens
                    self.completion_tokens += completion_tokens
                    self.total_tokens += total_tokens
                    self.calls_count += 1
                    
                    # 计算成本（以GPT-4为例，实际应根据模型调整）
                    # GPT-4: $0.03/1K prompt tokens, $0.06/1K completion tokens
                    cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000
                    self.total_cost += cost
        except Exception as e:
            # 如果无法提取token信息，静默失败
            pass
    
    def get_usage_summary(self) -> dict:
        """获取token使用摘要"""
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "calls_count": self.calls_count,
            "estimated_cost_usd": round(self.total_cost, 4)
        }
    
    def reset(self):
        """重置统计信息"""
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.calls_count = 0


def create_llm(
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    verbose: bool = None,
    callbacks: list = None
) -> ChatOpenAI:
    """
    创建LangChain ChatOpenAI实例
    
    Args:
        model: 使用的模型名称，默认从配置读取
        temperature: 温度参数（0-1），控制随机性
        max_tokens: 最大生成token数
        verbose: 是否输出详细日志，默认从配置读取
        callbacks: 回调处理器列表
        
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
        "timeout": 60,
        "max_tokens": max_tokens,
        "openai_api_key": Config.OPENAI_API_KEY,
        "verbose": verbose
    }
    
    # 如果提供了callbacks，添加到参数中
    if callbacks:
        kwargs["callbacks"] = callbacks
    
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
