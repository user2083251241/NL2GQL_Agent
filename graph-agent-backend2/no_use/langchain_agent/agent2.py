"""
简化版图查询智能体 (Graph Query Agent v2)
基于LangChain ReAct模式的基础实现，保留核心功能
"""
from typing import Dict, Any
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from modules.database import HugeGraphDB
from modules.llm import ChatOpenAI
from .tools import create_tools


class SimpleGraphAgent:
    """
    简化版图查询智能体
    
    核心功能：
    1. 使用ReAct Agent处理自然语言查询
    2. 自动生成并执行Gremlin查询
    3. 返回查询结果
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
        
        # 创建工具
        self.tools = create_tools(db)
        
        # 创建Agent
        self.agent_executor = self._create_agent()
        
        print("✅ SimpleGraphAgent 初始化成功")
    
    def _create_agent(self) -> AgentExecutor:
        """
        创建ReAct Agent
        
        Returns:
            AgentExecutor实例
        """
        # 简化的系统提示词
        system_prompt = """你是一个图数据库查询助手。
你可以使用以下工具来帮助用户查询图数据库：

{tools}

请按照以下格式回答：
Thought: 我需要做什么
Action: 工具名称
Action Input: 工具输入
Observation: 工具返回结果
... (可以重复多次)
Thought: 我现在知道答案了
Final Answer: 最终答案

开始！"""
        
        # 创建Prompt模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}\n\n{agent_scratchpad}")
        ])
        
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
        获取数据库Schema信息
        
        Returns:
            Schema信息字典
        """
        return self.db.get_schema()
