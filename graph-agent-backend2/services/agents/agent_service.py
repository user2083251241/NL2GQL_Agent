"""
智能查询服务 - 提供基于Agent的自然语言查询能力

职责：
1. 管理Agent实例的生命周期（单例模式）
2. 处理用户自然语言查询
3. 协调LLM和数据库的交互
4. 返回格式化的查询结果
"""
from typing import Dict, Any, Optional
from .agent2 import GraphAgent
from modules.database.client import get_db
from modules.llm.client import get_llm


class AgentQueryService:
    """
    Agent查询服务
    
    使用单例模式管理Agent实例，避免重复初始化开销
    """
    
    _instance = None
    _agent = None
    _enable_self_correction = True  # 默认启用自我修正
    
    def __new__(cls, enable_self_correction: bool = True):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            # 存储配置参数
            cls._enable_self_correction = enable_self_correction
        return cls._instance
    
    def __init__(self, enable_self_correction: bool = True):
        """初始化服务（仅执行一次）
        
        Args:
            enable_self_correction: 是否启用自我修正功能，默认为True
        """
        if self._initialized:
            return
        
        #print("🔄 初始化AgentQueryService...")
        self.enable_self_correction = self.__class__._enable_self_correction
        self._initialize_agent()
        self._initialized = True
        #print("✅ AgentQueryService初始化完成")
    
    def _initialize_agent(self):
        """
        初始化Agent实例
        
        从基础设施层获取依赖并创建Agent
        """
        try:
            # 从基础设施层获取依赖
            llm = get_llm()
            db = get_db()
            
            # 创建Agent实例，传递自我修正开关
            self._agent = GraphAgent(
                llm=llm, 
                db=db, 
                enable_self_correction=self.enable_self_correction
            )
            
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
    
    def stream_query(self, user_query: str):
        """
        流式处理用户自然语言查询（生成器）
        
        Args:
            user_query: 用户的自然语言问题
            
        Yields:
            SSE格式的事件数据字典
        """
        if not self._agent:
            yield {
                "type": "error",
                "content": "Agent未初始化",
                "timestamp": self._get_timestamp()
            }
            return
        
        try:
            from .tools import StreamingCallbackHandler
            import threading
            import queue
            
            # 创建一个队列用于实时传递步骤
            step_queue = queue.Queue()
            
            # 创建回调处理器，传入外部队列
            callback_handler = StreamingCallbackHandler(step_queue=step_queue)
            
            # 在后台线程中执行Agent查询
            def run_agent():
                try:
                    result = self._agent.agent_executor.invoke({
                        "input": user_query
                    }, config={"callbacks": [callback_handler]})
                except Exception as e:
                    # 将错误也放入队列
                    step_queue.put({
                        "type": "error",
                        "content": f"查询执行失败: {str(e)}",
                        "timestamp": self._get_timestamp()
                    })
                finally:
                    # 标记完成
                    step_queue.put(None)
            
            # 启动后台线程
            agent_thread = threading.Thread(target=run_agent, daemon=True)
            agent_thread.start()
            
            # 从队列中实时读取步骤并yield
            while True:
                try:
                    step = step_queue.get(timeout=1.0)
                    
                    if step is None:
                        # 收到结束信号
                        break
                    
                    # 立即yield这个步骤
                    yield step
                    
                except queue.Empty:
                    # 超时，继续等待
                    continue
            
            # 等待线程结束
            agent_thread.join(timeout=5.0)
            
        except Exception as e:
            error_msg = str(e)
            
            yield {
                "type": "error",
                "content": f"查询执行失败: {error_msg}",
                "timestamp": self._get_timestamp()
            }

    def _get_timestamp(self):
        """获取当前时间戳"""
        import time
        return int(time.time())

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
def get_agent_service(enable_self_correction: bool = True) -> AgentQueryService:
    """获取AgentQueryService单例实例
    
    Args:
        enable_self_correction: 是否启用自我修正功能，默认为True
        
    Returns:
        AgentQueryService实例
    """
    # 注意：由于是单例模式，第一次调用时的参数会生效
    # 后续调用即使传入不同参数也不会改变已初始化的实例
    return AgentQueryService(enable_self_correction=enable_self_correction)