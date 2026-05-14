"""
自定义Tools定义
为Agent提供执行Gremlin查询和获取Schema的能力
"""
import json
import os
from langchain.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field, validator
from modules.database.client import HugeGraphDB
from langchain_core.prompts import ChatPromptTemplate
from modules.llm.client import get_llm
from langchain_core.callbacks import BaseCallbackHandler
import queue
import threading


# ==================== SSE流式回调处理器 ====================

class StreamingCallbackHandler(BaseCallbackHandler):
    """
    流式回调处理器 - 捕获Agent执行过程中的所有输出
    
    用于SSE流式响应，实时推送Agent的思考过程到前端
    """
    
    def __init__(self):
        self.steps = []
        self.current_step = None
        self._queue = queue.Queue()
        self._finished = False
    
    def on_agent_action(self, action, **kwargs):
        """当Agent决定执行某个动作时触发"""
        step = {
            "type": "action",
            "content": f"🔧 执行工具: {action.tool}\n参数: {action.tool_input}",
            "timestamp": self._get_timestamp()
        }
        self.steps.append(step)
        self._queue.put(step)  # 立即放入队列
        print(f"\n{step['content']}")  # 同时输出到控制台
    
    def on_tool_end(self, output: str, **kwargs):
        """当工具执行完成时触发"""
        step = {
            "type": "observation",
            "content": f"📋 工具返回:\n{output[:500]}{'...' if len(output) > 500 else ''}",
            "timestamp": self._get_timestamp()
        }
        self.steps.append(step)
        self._queue.put(step)  # 立即放入队列
        print(f"\n{step['content']}")  # 同时输出到控制台
    
    def on_agent_finish(self, finish, **kwargs):
        """当Agent执行完成时触发"""
        step = {
            "type": "final_answer",
            "content": finish.return_values.get("output", ""),
            "timestamp": self._get_timestamp()
        }
        self.steps.append(step)
        self._queue.put(step)  # 立即放入队列
        print(f"\n✅ 最终答案:\n{step['content']}")  # 同时输出到控制台
    
    def on_chain_start(self, serialized, inputs, **kwargs):
        """当链开始时触发"""
        if 'input' in inputs:
            step = {
                "type": "thought",
                "content": f"💭 思考中...",
                "timestamp": self._get_timestamp()
            }
            self.steps.append(step)
            self._queue.put(step)  # 立即放入队列
            print(f"\n{step['content']}")  # 同时输出到控制台
    
    def on_text(self, text: str, **kwargs):
        """当有文本输出时触发（LLM生成的中间内容）"""
        if text.strip():
            step = {
                "type": "thought",
                "content": text[:300],
                "timestamp": self._get_timestamp()
            }
            self.steps.append(step)
            self._queue.put(step)  # 立即放入队列
            print(f"\n💬 LLM输出: {text[:200]}")  # 同时输出到控制台
    
    def on_chain_error(self, error, **kwargs):
        """当链执行出错时触发"""
        step = {
            "type": "error",
            "content": f"❌ 错误: {str(error)}",
            "timestamp": self._get_timestamp()
        }
        self.steps.append(step)
        self._queue.put(step)  # 立即放入队列
        print(f"\n{step['content']}")  # 同时输出到控制台
    
    def mark_finished(self):
        """标记处理完成"""
        self._finished = True
        self._queue.put(None)  # 发送结束信号
    
    def get_next_step(self, timeout=1.0):
        """获取下一个步骤（阻塞等待）"""
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def _get_timestamp(self):
        """获取当前时间戳"""
        import time
        return int(time.time())


# ==================== Schema映射表加载函数 ====================

def load_schema_mapping() -> dict:
    """
    加载schema映射表，提供英文标签到中文语义的映射
    
    Returns:
        包含映射关系的字典
    """
    try:
        mapping_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'mapping', 'schema_mapping.json')
        if os.path.exists(mapping_path):
            with open(mapping_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"⚠️ Schema映射表未找到: {mapping_path}")
            return {}
    except Exception as e:
        print(f"⚠️ 加载schema映射表失败: {e}")
        return {}


def enhance_schema_with_mapping(schema_info: str, mapping: dict) -> str:
    """
    使用映射表增强schema信息，添加中文语义说明
    
    Args:
        schema_info: 原始schema信息字符串
        mapping: schema映射字典
        
    Returns:
        增强后的schema信息字符串
    """
    if not mapping:
        return schema_info
    
    enhanced_parts = []
    lines = schema_info.split('\n')
    
    for line in lines:
        enhanced_line = line
        
        # 处理顶点标签行
        if line.strip().startswith('- ') and '(属性:' in line:
            # 提取顶点标签名
            label_part = line.split('(属性:')[0].strip()
            if label_part.startswith('- '):
                label_name = label_part[2:]  # 移除 "- "
                # 查找中文描述
                if label_name in mapping.get('vertices', {}):
                    chinese_desc = mapping['vertices'][label_name]['description']
                    enhanced_line = f"{line} [中文: {chinese_desc}]"
        
        elif line.strip().startswith('- ') and '(属性:' not in line and not line.strip().endswith('(无)'):
            # 处理无属性的顶点或边标签
            label_part = line.strip()[2:]  # 移除 "- "
            # 检查是否是顶点标签
            if label_part in mapping.get('vertices', {}):
                chinese_desc = mapping['vertices'][label_part]['description']
                enhanced_line = f"{line} [中文: {chinese_desc}]"
            # 检查是否是边标签
            elif label_part in mapping.get('edges', {}):
                chinese_desc = mapping['edges'][label_part]['description']
                enhanced_line = f"{line} [中文: {chinese_desc}]"
        
        enhanced_parts.append(enhanced_line)
    
    # 添加字段映射速查表
    if mapping and 'field_mapping' in mapping:
        enhanced_parts.append("\n📋 字段中文映射速查:")
        for field, chinese_meaning in mapping['field_mapping'].items():
            enhanced_parts.append(f"  - {field}: {chinese_meaning}")
    
    return '\n'.join(enhanced_parts)


# ==================== Tool输入模型 ====================

class ExecuteGremlinInput(BaseModel):
    """执行Gremlin查询的输入参数"""
    gremlin_query: str = Field(#gremlin_query是Gremlin查询语句的字符串，必填项
        description="要执行的Gremlin查询语句，必须符合HugeGraph语法规范"
    )


class GetSchemaInput(BaseModel):
    """获取Schema信息的输入参数"""
    enable_semantic_enhancement: Optional[bool] = Field(
        default=False,
        description="是否启用中文语义增强，默认为False"
    )
    
    @validator('enable_semantic_enhancement', pre=True)
    def parse_semantic_enhancement(cls, v):
        """解析语义增强参数，支持字符串和JSON格式"""
        if isinstance(v, str):
            try:
                # 尝试解析JSON字符串
                parsed = json.loads(v)
                if isinstance(parsed, dict) and 'enable_semantic_enhancement' in parsed:
                    return bool(parsed['enable_semantic_enhancement'])
                elif isinstance(parsed, bool):
                    return parsed
                else:
                    return bool(parsed)
            except (json.JSONDecodeError, TypeError):
                # 如果不是有效的JSON，尝试直接转换为布尔值
                return v.lower() in ('true', '1', 'yes', 'on')
        return bool(v) if v is not None else False


class AnalyzeErrorInput(BaseModel):
    """分析错误的输入参数"""
    original_question: str = Field(
        description="用户的原始问题"
    )
    failed_gremlin: str = Field(
        description="执行失败的Gremlin查询语句"
    )
    error_message: str = Field(
        description="Gremlin执行返回的错误信息"
    )


# ==================== Execute Gremlin Tool ====================

class ExecuteGremlinTool(BaseTool):
    """
    执行Gremlin查询的工具
    
    用途：
    - 在HugeGraph数据库中执行Gremlin查询
    - 返回查询结果或错误信息
    """
    
    name: str = "execute_gremlin"
    description: str = (
        "在HugeGraph图数据库中执行Gremlin查询。"
        "输入必须是合法的Gremlin语句。"
        "返回查询结果数据或错误信息。"
    )
    args_schema: Type[BaseModel] = ExecuteGremlinInput
    db: HugeGraphDB = None

    def __init__(self, db: HugeGraphDB):
        """初始化工具，注入数据库实例"""
        super().__init__(db=db)
    
    def _run(self, gremlin_query: str) -> str:
        """
        同步执行Gremlin查询
        
        Args:
            gremlin_query: Gremlin查询语句
            
        Returns:
            格式化的查询结果字符串
        """
        try:
            # 执行查询
            result = self.db.execute_gremlin(gremlin_query)
            
            # 格式化返回结果
            if result["success"]:
                data = result["data"]
                count = result.get("count", len(data) if isinstance(data, list) else 1)
                
                return (
                    f"✅ 查询成功\n"
                    f"   结果数量: {count}\n"
                    f"   数据: {data}"
                )
            else:
                error_msg = result.get("error", "未知错误")
                return f"❌ 查询失败: {error_msg}"
                
        except Exception as e:
            return f"❌ 执行异常: {str(e)}"
    
    async def _arun(self, gremlin_query: str) -> str:
        """异步执行（目前同步实现）"""
        return self._run(gremlin_query)


# ==================== Get Schema Tool ====================

class GetSchemaTool(BaseTool):
    """
    获取图数据库Schema信息的工具
    
    用途：
    - 获取所有顶点标签、边标签和属性定义
    - 帮助Agent理解数据库结构
    - 用于模式链接（Schema Linking）
    - 集成中文语义映射增强理解能力
    """
    
    name: str = "get_schema_info"
    description: str = (
        "获取HugeGraph图数据库的完整Schema信息，"
        "包括所有顶点标签、边标签和它们的属性定义，"
        "并提供中文语义映射帮助理解数据含义。"
        "在生成Gremlin查询前，应该先调用此工具了解数据库结构。"
        "可以通过enable_semantic_enhancement参数控制是否启用中文语义增强。"
    )
    args_schema: Type[BaseModel] = GetSchemaInput
    db: HugeGraphDB = None

    def __init__(self, db: HugeGraphDB):
        """初始化工具，注入数据库实例"""
        super().__init__(db=db)
    
    def _run(self, enable_semantic_enhancement: bool = False) -> str:
        """
        获取Schema信息并根据参数决定是否增强中文语义
        
        Args:
            enable_semantic_enhancement: 是否启用中文语义增强
            
        Returns:
            格式化的Schema信息字符串（可选择包含中文映射）
        """
        # 强制禁用语义增强功能，用于消融实验
        enable_semantic_enhancement = True
        
        try:
            # 获取Schema
            schema = self.db.get_schema()
            
            # 检查是否有错误
            if "error" in schema:
                return f"❌ 获取Schema失败: {schema['error']}"
            
            # 格式化输出
            vertex_labels = schema.get("vertex_labels", [])
            edge_labels = schema.get("edge_labels", [])
            properties = schema.get("properties", {})
            
            output_parts = []
            
            # 顶点标签
            output_parts.append("📊 顶点标签:")
            if vertex_labels:
                for label in vertex_labels:
                    props = properties.get(label, [])
                    if props:
                        output_parts.append(f"  - {label}(属性: {', '.join(props)})")
                    else:
                        output_parts.append(f"  - {label}")
            else:
                output_parts.append("  (无)")
            
            # 边标签
            output_parts.append("\n🔗 边标签:")
            if edge_labels:
                for label in edge_labels:
                    output_parts.append(f"  - {label}")
            else:
                output_parts.append("  (无)")
            
            # 基础schema信息
            basic_schema_info = "\n".join(output_parts)
            
            # 根据开关决定是否增强信息
            if enable_semantic_enhancement:
                mapping = load_schema_mapping()
                enhanced_schema_info = enhance_schema_with_mapping(basic_schema_info, mapping)
                return enhanced_schema_info
            else:
                return basic_schema_info
            
        except Exception as e:
            return f"❌ 获取Schema异常: {str(e)}"
    
    async def _arun(self, enable_semantic_enhancement: bool = True) -> str:
        """异步执行（目前同步实现）"""
        return self._run(enable_semantic_enhancement)


# ==================== Analyze Error Tool ====================

class AnalyzeErrorTool(BaseTool):
    """
    分析Gremlin查询错误并提供修正建议的工具
    
    用途：
    - 分析执行失败的Gremlin查询的错误原因
    - 基于数据库Schema提供具体的修正建议
    - 生成修正后的Gremlin查询语句
    """
    
    name: str = "analyze_and_correct_error"
    description: str = (
        "分析Gremlin查询执行失败的原因，并基于数据库Schema提供修正建议。"
        "输入包括原始问题、失败的Gremlin语句和错误信息。"
        "返回详细的错误分析和修正后的Gremlin查询。"
    )
    args_schema: Type[BaseModel] = AnalyzeErrorInput
    db: HugeGraphDB = None

    def __init__(self, db: HugeGraphDB):
        """初始化工具，注入数据库实例"""
        super().__init__(db=db)
    
    def _run(self, original_question: str, failed_gremlin: str, error_message: str) -> str:
        """
        分析错误并生成修正建议
        
        Args:
            original_question: 用户的原始问题
            failed_gremlin: 执行失败的Gremlin查询
            error_message: 错误信息
            
        Returns:
            错误分析和修正建议
        """
        try:
            # 获取当前数据库Schema
            schema = self.db.get_schema()
            if "error" in schema:
                schema_info = f"获取Schema失败: {schema['error']}"
            else:
                # 简化Schema信息用于提示词
                vertex_labels = schema.get("vertex_labels", [])
                edge_labels = schema.get("edge_labels", [])
                properties = schema.get("properties", {})
                
                schema_parts = []
                schema_parts.append("顶点标签:")
                for label in vertex_labels:
                    props = properties.get(label, [])
                    if props:
                        schema_parts.append(f"- {label} (属性: {', '.join(props)})")
                    else:
                        schema_parts.append(f"- {label}")
                
                schema_parts.append("\n边标签:")
                for label in edge_labels:
                    schema_parts.append(f"- {label}")
                
                schema_info = "\n".join(schema_parts)
            
            # 创建错误分析提示词
            correction_prompt = ChatPromptTemplate.from_template(
                """之前的Gremlin查询执行失败，需要修正。

用户原始问题：{original_question}
之前生成的Gremlin：{failed_gremlin}
错误信息：{error_message}
数据库Schema：{schema_info}

请分析：
1. 错误原因是什么？（例如：语法错误、标签不存在、属性不存在等）
2. 如何修正Gremlin查询？
3. 修正后的查询应该是什么？

请按以下格式回答：
错误分析：[详细分析错误原因]
修正建议：[具体的修正步骤]
修正后的Gremlin：[完整的修正后Gremlin查询语句]"""
            )
            
            # 使用LLM进行错误分析
            llm = get_llm()
            prompt = correction_prompt.format(
                original_question=original_question,
                failed_gremlin=failed_gremlin,
                error_message=error_message,
                schema_info=schema_info
            )
            
            response = llm.invoke(prompt)
            
            return f"🔍 错误分析完成\n{response.content}"
            
        except Exception as e:
            return f"❌ 错误分析失败: {str(e)}"
    
    async def _arun(self, original_question: str, failed_gremlin: str, error_message: str) -> str:
        """异步执行（目前同步实现）"""
        return self._run(original_question, failed_gremlin, error_message)


# ==================== 工具工厂函数 ====================

def create_tools(db: HugeGraphDB, enable_self_correction: bool = True) -> list:
    """
    创建Agent可用的所有工具
    
    Args:
        db: HugeGraph数据库实例
        enable_self_correction: 是否启用自我修正功能（包含错误分析工具），默认为True
        
    Returns:
        工具列表
    """
    tools = [
        ExecuteGremlinTool(db=db),
        GetSchemaTool(db=db),
    ]
    
    if enable_self_correction:
        tools.append(AnalyzeErrorTool(db=db))
        
    return tools