"""
自定义Tools定义
为Agent提供执行Gremlin查询和获取Schema的能力
"""
from langchain.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
from modules.database.client import HugeGraphDB


# ==================== Tool输入模型 ====================

class ExecuteGremlinInput(BaseModel):
    """执行Gremlin查询的输入参数"""
    gremlin_query: str = Field(#gremlin_query是Gremlin查询语句的字符串，必填项
        description="要执行的Gremlin查询语句，必须符合HugeGraph语法规范"
    )


class GetSchemaInput(BaseModel):
    """获取Schema信息的输入参数（通常不需要参数）"""
    dummy: Optional[str] = Field(
        default="",
        description="占位符参数，实际使用时不需要传入"
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
    """
    
    name: str = "get_schema_info"
    description: str = (
        "获取HugeGraph图数据库的完整Schema信息，"
        "包括所有顶点标签、边标签和它们的属性定义。"
        "在生成Gremlin查询前，应该先调用此工具了解数据库结构。"
    )
    args_schema: Type[BaseModel] = GetSchemaInput
    db: HugeGraphDB = None

    def __init__(self, db: HugeGraphDB):
        """初始化工具，注入数据库实例"""
        super().__init__(db=db)
    
    def _run(self, dummy: str = "") -> str:
        """
        获取Schema信息
        
        Returns:
            格式化的Schema信息字符串
        """
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
            
            return "\n".join(output_parts)
            
        except Exception as e:
            return f"❌ 获取Schema异常: {str(e)}"
    
    async def _arun(self, dummy: str = "") -> str:
        """异步执行（目前同步实现）"""
        return self._run(dummy)


# ==================== 工具工厂函数 ====================

def create_tools(db: HugeGraphDB) -> list:
    """
    创建Agent可用的所有工具
    
    Args:
        db: HugeGraph数据库实例
        
    Returns:
        工具列表
    """
    return [
        ExecuteGremlinTool(db=db),
        GetSchemaTool(db=db),
    ]
