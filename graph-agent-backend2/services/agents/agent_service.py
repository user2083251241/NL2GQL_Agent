"""
智能查询服务 - 提供基于Agent的自然语言查询能力

职责：
1. 管理Agent实例的生命周期（单例模式）
2. 处理用户自然语言查询
3. 协调LLM和数据库的交互
4. 返回格式化的查询结果
"""
from typing import Dict, Any, Optional
from .agent2 import SimpleGraphAgent
from modules.database.client import get_db
from modules.llm.client import get_llm


class AgentQueryService:
    """
    Agent查询服务
    
    使用单例模式管理Agent实例，避免重复初始化开销
    """
    
    _instance = None
    _agent = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化服务（仅执行一次）"""
        if self._initialized:
            return
        
        print("🔄 初始化AgentQueryService...")
        self._initialize_agent()
        self._initialized = True
        print("✅ AgentQueryService初始化完成")
    
    def _initialize_agent(self):
        """
        初始化Agent实例
        
        从基础设施层获取依赖并创建Agent
        """
        try:
            # 从基础设施层获取依赖
            llm = get_llm()
            db = get_db()
            
            # 创建Agent实例
            self._agent = SimpleGraphAgent(llm=llm, db=db)
            
        except Exception as e:
            print(f"❌ Agent初始化失败: {e}")
            raise
    
    def query(self, user_query: str) -> Dict[str, Any]:
        """
        处理用户自然语言查询
        
        Args:
            user_query: 用户的自然语言问题
            
        Returns:
            格式化的查询结果:
            {
                "success": bool,
                "question": str,
                "answer": str,
                "error": str (可选)
            }
        """
        if not self._agent:
            return {
                "success": False,
                "question": user_query,
                "answer": None,
                "error": "Agent未初始化"
            }
        
        try:
            # 调用Agent执行业务逻辑
            result = self._agent.query(user_query)
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 查询执行失败: {error_msg}")
            
            return {
                "success": False,
                "question": user_query,
                "answer": None,
                "error": f"查询执行失败: {error_msg}"
            }
    
    def get_schema(self) -> Dict[str, Any]:
        """
        获取数据库Schema信息
        
        Returns:
            Schema信息字典
        """
        if not self._agent:
            return {
                "vertex_labels": [],
                "edge_labels": [],
                "properties": {},
                "error": "Agent未初始化"
            }
        
        return self._agent.get_schema()
    
    @classmethod
    def reset(cls):
        """重置服务实例（用于测试或重新配置）"""
        cls._instance = None
        cls._agent = None
        print("🔄 AgentQueryService已重置")


# 便捷函数：获取服务实例
def get_agent_service() -> AgentQueryService:
    """获取AgentQueryService单例实例"""
    return AgentQueryService()
