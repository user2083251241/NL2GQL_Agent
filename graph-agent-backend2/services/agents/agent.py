"""
图查询智能体 (Graph Query Agent)
基于LangChain ReAct模式实现自然语言到Gremlin的转换和执行
"""
from typing import Dict, Any, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from modules.database.client import HugeGraphDB
from modules.llm.client import ChatOpenAI
from .tools import create_tools
from .prompts import (
    get_system_prompt,
    create_text_to_gremlin_prompt,
    create_result_explanation_prompt,
    create_correction_prompt
)


class GraphQueryAgent:
    """
    图查询智能体
    
    工作流程：
    1. 获取数据库Schema（模式链接）
    2. 使用ReAct Agent生成并执行Gremlin查询
    3. 解释查询结果
    4. 失败时自我修正（最多2次重试）
    """

    def __init__(self, llm: ChatOpenAI, db: HugeGraphDB, max_retries: int = 2):
        """
        初始化Agent
        
        Args:
            llm: LangChain LLM实例
            db: HugeGraph数据库实例
            max_retries: 最大重试次数（自我修正）
        """
        self.llm = llm
        self.db = db
        self.max_retries = max_retries
        
        # 创建工具
        self.tools = create_tools(db)
        
        # 创建Agent
        self.agent_executor = self._create_agent()
        
        # 创建结果解释链
        self.explanation_chain = create_result_explanation_prompt() | llm
        
        print("✅ GraphQueryAgent 初始化成功")
    
    def _create_agent(self) -> AgentExecutor:
        """
        创建ReAct Agent
        
        Returns:
            AgentExecutor实例
        """
        # 构建ReAct Prompt
        system_prompt = get_system_prompt()
        
        # ReAct框架的Prompt模板
        react_template = f"""{system_prompt}

你可以使用以下工具：

{{tools}}

工具名称列表: {{tool_names}}

使用工具的格式：
```
Thought: 我需要做什么
Action: 工具名称 (必须是 {{tool_names}} 中的一个)
Action Input: 工具输入
Observation: 工具返回结果
... (可以重复Thought/Action/Observation多次)
Thought: 我现在知道最终答案
Final Answer: 最终答案
```

开始！

{{input}}
{{agent_scratchpad}}"""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(react_template)
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
            verbose=True,  # 显示详细思考过程
            max_iterations=10,  # 最大迭代次数
            handle_parsing_errors=True,  # 处理解析错误
            return_intermediate_steps=True  # 返回中间步骤
        )
        
        return agent_executor
    
    def process_query(self, question: str) -> Dict[str, Any]:
        """
        处理用户查询（主入口）
        
        Args:
            question: 用户的自然语言问题
            
        Returns:
            包含查询结果的字典:
            {
                "success": bool,
                "question": str,
                "gremlin": str,
                "result": Any,
                "explanation": str,
                "retries": int,
                "error": str (可选)
            }
        """
        print(f"\n🔍 处理查询: {question}")
        
        # 尝试执行查询（带重试）
        for attempt in range(1, self.max_retries + 1):
            print(f"\n--- 第 {attempt} 次尝试 ---")
            
            try:
                # 执行Agent
                agent_result = self.agent_executor.invoke({
                    "input": question
                })
                
                # 提取结果
                final_answer = agent_result.get("output", "")
                intermediate_steps = agent_result.get("intermediate_steps", [])
                
                # 从中间步骤中提取Gremlin和查询结果
                gremlin, query_result = self._extract_gremlin_and_result(intermediate_steps)
                
                # 如果查询成功，解释结果
                if query_result and query_result.get("success"):
                    explanation = self._explain_result(question, gremlin, query_result)
                    
                    return {
                        "success": True,
                        "question": question,
                        "gremlin": gremlin,
                        "result": query_result.get("data"),
                        "explanation": explanation,
                        "retries": attempt,
                        "intermediate_steps": intermediate_steps
                    }
                else:
                    # 查询失败，准备重试
                    error_msg = query_result.get("error", "未知错误") if query_result else "未执行查询"
                    print(f"⚠️ 查询失败: {error_msg}")
                    
                    if attempt < self.max_retries:
                        print("🔄 准备自我修正...")
                        # 这里可以添加更复杂的修正逻辑
                        continue
                    else:
                        return {
                            "success": False,
                            "question": question,
                            "gremlin": gremlin,
                            "result": None,
                            "explanation": f"查询失败，已重试{self.max_retries}次",
                            "retries": attempt,
                            "error": error_msg
                        }
                        
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Agent执行异常: {error_msg}")
                
                if attempt < self.max_retries:
                    print("🔄 准备重试...")
                    continue
                else:
                    return {
                        "success": False,
                        "question": question,
                        "gremlin": None,
                        "result": None,
                        "explanation": f"处理失败: {error_msg}",
                        "retries": attempt,
                        "error": error_msg
                    }
        
        # 所有重试都失败
        return {
            "success": False,
            "question": question,
            "gremlin": None,
            "result": None,
            "explanation": f"查询失败，已重试{self.max_retries}次",
            "retries": self.max_retries,
            "error": "达到最大重试次数"
        }
    
    def _extract_gremlin_and_result(self, intermediate_steps: list) -> tuple:
        """
        从中间步骤中提取Gremlin查询和结果
        
        Args:
            intermediate_steps: Agent的中间执行步骤
            
        Returns:
            (gremlin_query, query_result) 元组
        """
        gremlin = None
        query_result = {"success": False, "data": None}
        
        # 遍历中间步骤，查找execute_gremlin工具的调用
        for step in intermediate_steps:
            action, observation = step
            
            # 检查是否是execute_gremlin工具
            if action.tool == "execute_gremlin":
                gremlin = action.tool_input.get("gremlin_query", "")
                
                # 解析观察结果 (observation 现在是字符串)
                if isinstance(observation, str):
                    if "✅ 查询成功" in observation:
                        # 尝试从字符串中提取数据部分
                        # 格式通常为: "✅ 查询成功\n   结果数量: X\n   数据: [...]"
                        lines = observation.split('\n')
                        data_line = next((line for line in lines if line.strip().startswith("数据:")), None)
                        if data_line:
                            try:
                                # 提取 "数据: " 后面的内容并尝试解析为 Python 对象
                                data_str = data_line.split("数据: ", 1)[1]
                                # 注意：这里简单处理，实际生产中应使用更安全的解析方式
                                import ast
                                data_content = ast.literal_eval(data_str)
                                query_result = {"success": True, "data": data_content}
                            except:
                                query_result = {"success": True, "data": observation}
                        else:
                            query_result = {"success": True, "data": observation}
                    elif "❌" in observation:
                        query_result = {"success": False, "error": observation}
                elif isinstance(observation, dict):
                    # 兼容旧版本或特殊情况
                    query_result = observation
        
        return gremlin, query_result
    
    def _explain_result(self, question: str, gremlin: str, result: Dict) -> str:
        """
        解释查询结果
        
        Args:
            question: 原始问题
            gremlin: 执行的Gremlin查询
            result: 查询结果
            
        Returns:
            自然语言解释
        """
        try:
            # 使用LLM解释结果
            chain = self.explanation_chain
            response = chain.invoke({
                "question": question,
                "gremlin": gremlin,
                "result": result.get("data", [])
            })
            
            return response.content
            
        except Exception as e:
            # 如果解释失败，返回简单说明
            data = result.get("data", [])
            count = len(data) if isinstance(data, list) else 1
            return f"查询完成，返回{count}条结果。"
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        获取数据库Schema信息
        
        Returns:
            Schema信息字典
        """
        return self.db.get_schema()