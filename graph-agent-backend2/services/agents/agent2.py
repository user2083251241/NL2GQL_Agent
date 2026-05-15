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
    5. 支持错误分析和自我修正机制（可选）
    """
    
    def __init__(self, llm: ChatOpenAI, db: HugeGraphDB, enable_self_correction: bool = True):
        """
        初始化Agent
        
        Args:
            llm: LangChain LLM实例
            db: HugeGraph数据库实例
            enable_self_correction: 是否启用自我修正功能，默认为True
        """
        self.llm = llm
        self.db = db
        self.enable_self_correction = enable_self_correction
        
        # 创建工具（根据开关决定是否包含analyze_and_correct_error工具）
        self.tools = create_tools(db, enable_self_correction=enable_self_correction)
        
        # 创建Agent
        self.agent_executor = self._create_agent()
        
        #print(f"✅ GraphAgent 初始化成功 (自我修正: {'启用' if enable_self_correction else '禁用'})")
    
    def _create_agent(self) -> AgentExecutor:
        """
        创建ReAct Agent
        
        Returns:
            AgentExecutor实例
        """
        # 使用prompts.py中定义的规范Prompt模板，传递自我修正开关
        prompt = create_react_agent_prompt(enable_self_correction=self.enable_self_correction)
        
        # 创建ReAct Agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # 创建Agent执行器，根据是否启用自我修正调整迭代次数
        max_iterations = 8 if self.enable_self_correction else 5
        
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=max_iterations,
            handle_parsing_errors=True,
            early_stopping_method="generate"
        )
        
        return agent_executor
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        处理用户查询（支持自我修正）
        
        Args:
            question: 用户的自然语言问题
            
        Returns:
            包含查询结果的字典:
            {
                "success": bool,
                "question": str,
                "answer": str,
                "error": str (可选),
                "corrections_attempted": int (可选，尝试修正的次数)
            }
        """
        print(f"\n🔍 处理查询: {question}")
        
        try:
            # 执行Agent
            # Agent会根据需要自动调用get_schema_info工具获取数据库结构
            # 如果查询失败且启用了自我修正，Agent可以调用analyze_and_correct_error工具进行自我修正
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
    
    def extract_gremlin_from_error(self, error_observation: str) -> tuple:
        """
        从错误观察结果中提取原始Gremlin查询和错误信息
        
        Args:
            error_observation: 工具返回的错误观察结果
            
        Returns:
            (gremlin_query, error_message) 元组
        """
        # 这是一个辅助方法，用于在需要时手动提取错误信息
        # 实际上，ReAct Agent会自动处理这些信息
        lines = error_observation.split('\n')
        gremlin_query = ""
        error_message = ""
        
        # 简单的提取逻辑（实际使用中由LLM处理）
        for line in lines:
            if line.startswith("Gremlin查询："):
                gremlin_query = line.replace("Gremlin查询：", "").strip()
            elif "❌" in line or "错误" in line:
                error_message = line.strip()
        
        return gremlin_query, error_message