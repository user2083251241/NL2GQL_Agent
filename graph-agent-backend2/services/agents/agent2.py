"""
简化版图查询智能体 (Graph Query Agent v2)
基于LangChain ReAct模式的基础实现，保留核心功能
"""
from typing import Dict, Any
from langchain.agents import AgentExecutor, create_react_agent
from modules.database.client import HugeGraphDB
from modules.llm.client import ChatOpenAI
from .tools import create_tools
from .prompts import create_react_agent_prompt


class GraphAgent:
    """
    简化版图查询智能体
    
    核心功能：
    1. 使用ReAct Agent处理自然语言查询
    2. 自动生成并执行Gremlin查询
    3. 返回查询结果
    4. 自主调用工具获取Schema信息（无需手动注入）
    """
    
    def __init__(self, llm: ChatOpenAI, db: HugeGraphDB):
        """
        初始化Agent
        
        Args:
            llm: LangChain LLM实例
            db: HugeGraph数据库实例
        """
        self.llm = llm
        self.db = db
        
        # 创建工具（包含get_schema_info和execute_gremlin）
        self.tools = create_tools(db)
        
        # 创建Agent
        self.agent_executor = self._create_agent()
        
        print("✅ GraphAgent 初始化成功")
    
    def _create_agent(self) -> AgentExecutor:
        """
        创建ReAct Agent
        
        Returns:
            AgentExecutor实例
        """
        # 使用prompts.py中定义的规范Prompt模板
        # 注意：这里不再手动注入schema信息，让Agent自主调用get_schema_info工具
        prompt = create_react_agent_prompt()
        
        # 创建ReAct Agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # 创建Agent执行器
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
        
        return agent_executor
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        处理用户查询（简化版）
        
        Args:
            question: 用户的自然语言问题
            
        Returns:
            包含查询结果的字典:
            {
                "success": bool,
                "question": str,
                "answer": str,
                "error": str (可选)
            }
        """
        print(f"\n🔍 处理查询: {question}")
        
        try:
            # 执行Agent
            # Agent会根据需要自动调用get_schema_info工具获取数据库结构
            result = self.agent_executor.invoke({
                "input": question
            })
            
            # 提取最终答案
            answer = result.get("output", "未获取到答案")
            
            return {
                "success": True,
                "question": question,
                "answer": answer
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 查询失败: {error_msg}")
            
            return {
                "success": False,
                "question": question,
                "answer": None,
                "error": error_msg
            }
    
    def get_schema(self) -> Dict[str, Any]:
        """
        获取数据库Schema信息（供外部调用）
        
        Returns:
            Schema信息字典
        """
        return self.db.get_schema()
