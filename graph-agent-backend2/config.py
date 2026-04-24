import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

class Config:
    """统一配置类，所有配置项集中管理"""
    
    # ========== HugeGraph 数据库配置 ==========
    HUGEGRAPH_HOST = os.getenv("HUGEGRAPH_HOST", "127.0.0.1")
    HUGEGRAPH_PORT = int(os.getenv("HUGEGRAPH_PORT", 8080))
    HUGEGRAPH_USER = os.getenv("HUGEGRAPH_USER", "admin")
    HUGEGRAPH_PWD = os.getenv("HUGEGRAPH_PWD", "admin")
    HUGEGRAPH_GRAPH = os.getenv("HUGEGRAPH_GRAPH", "hugegraph")
    # 可选：HugeGraph 1.5+ 支持 GraphSpace，默认留空
    HUGEGRAPH_GRAPHSPACE = os.getenv("HUGEGRAPH_GRAPHSPACE", None)
    
    # ========== LLM 配置（以 OpenAI 为例） ==========
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    # 可选：自定义 API 地址（如代理或国内中转）
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", None)
    
    # ========== LangChain 配置 ==========
    LANGCHAIN_VERBOSE = os.getenv("LANGCHAIN_VERBOSE", "False").lower() == "true"
    
    # ========== Flask 应用配置 ==========
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    
    # ========== 验证必需配置 ==========
    @classmethod
    def validate(cls):
        """验证必需的配置项是否已设置"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY 未配置，请在 .env 文件中设置")
        return True
