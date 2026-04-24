"""
数据库模块 - HugeGraph客户端封装
提供Gremlin执行和Schema提取功能
"""
from pyhugegraph.client import PyHugeClient
from config import Config
from typing import Dict, List, Any, Optional


class HugeGraphDB:
    """
    HugeGraph数据库客户端（单例模式）
    
    功能：
    1. 执行Gremlin查询
    2. 获取图Schema信息（顶点标签、边标签、属性）
    """
    
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls) 
            cls._instance._initialized = False  
        return cls._instance
    
    def __init__(self):
        """初始化数据库连接（仅执行一次）"""
        if self._initialized:#
            return
        
        try:
            self._client = PyHugeClient(
                ip=Config.HUGEGRAPH_HOST,
                port=Config.HUGEGRAPH_PORT,
                user=Config.HUGEGRAPH_USER,
                pwd=Config.HUGEGRAPH_PWD,
                graph=Config.HUGEGRAPH_GRAPH
            )
            self._initialized = True
            print(f"✅ HugeGraph连接成功: {Config.HUGEGRAPH_HOST}:{Config.HUGEGRAPH_PORT}")
        except Exception as e:
            print(f"❌ HugeGraph连接失败: {e}")
            raise
    
    def execute_gremlin(self, query: str) -> Dict[str, Any]:
        """
        执行Gremlin查询
        
        Args:
            query: Gremlin查询语句
            
        Returns:
            包含查询结果的字典:
            {
                "success": bool,
                "data": list,
                "error": str (可选)
            }
        """
        try:
            result = self._client.gremlin().exec(query)
            data = result.get("data", [])
            
            return {
                "success": True,
                "data": data,
                "count": len(data) if isinstance(data, list) else 1
            }
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Gremlin执行错误: {error_msg}")
            print(f"   查询语句: {query}")
            
            return {
                "success": False,
                "data": [],
                "error": error_msg
            }
    
    def get_schema(self) -> Dict[str, Any]:
        """
        获取图数据库的完整Schema信息
        
        Returns:
            包含Schema信息的字典:
            {
                "vertex_labels": ["Person", "Company", ...],
                "edge_labels": ["knows", "works_at", ...],
                "properties": {
                    "Person": ["name", "age", ...],
                    "Company": ["name", "address", ...]
                }
            }
        """
        try:
            schema = {
                "vertex_labels": self._get_vertex_labels(),
                "edge_labels": self._get_edge_labels(),
                "properties": self._get_properties()
            }
            
            print(f"✅ Schema获取成功: {len(schema['vertex_labels'])}个顶点标签, "
                  f"{len(schema['edge_labels'])}个边标签")
            return schema
            
        except Exception as e:
            print(f"❌ Schema获取失败: {e}")
            return {
                "vertex_labels": [],
                "edge_labels": [],
                "properties": {},
                "error": str(e)
            }
    
    def _get_vertex_labels(self) -> List[str]:
        """获取所有顶点标签"""
        try:
            # 使用Gremlin查询所有顶点标签
            result = self.execute_gremlin("g.V().label().dedup()")
            if result["success"]:
                return result["data"]
            return []
        except:
            return []
    
    def _get_edge_labels(self) -> List[str]:
        """获取所有边标签"""
        try:
            # 使用Gremlin查询所有边标签
            result = self.execute_gremlin("g.E().label().dedup()")
            if result["success"]:
                return result["data"]
            return []
        except:
            return []
    
    def _get_properties(self) -> Dict[str, List[str]]:
        """
        获取每个标签的属性列表
        
        Returns:
            {
                "Person": ["name", "age", "city"],
                "Company": ["name", "address"]
            }
        """
        properties = {}
        
        try:
            # 获取所有顶点标签
            vertex_labels = self._get_vertex_labels()
            
            # 对每个标签，查询一个示例顶点来获取属性
            for label in vertex_labels:
                query = f"g.V().hasLabel('{label}').limit(1).elementMap()"
                result = self.execute_gremlin(query)
                
                if result["success"] and result["data"]:
                    # 从示例数据中提取属性键
                    sample = result["data"][0]
                    if isinstance(sample, dict):
                        # 过滤掉系统属性（id, label等）
                        props = [
                            key for key in sample.keys() 
                            if key not in ['id', 'label', '~id', '~label']
                        ]
                        properties[label] = props
        
        except Exception as e:
            print(f"⚠️ 获取属性信息时出错: {e}")
        
        return properties
    
    def get_schema_text(self) -> str:
        """
        获取格式化的Schema文本（用于Prompt）
        
        Returns:
            可读的Schema描述文本
        """
        schema = self.get_schema()
        
        text_parts = []
        
        # 顶点标签
        if schema["vertex_labels"]:
            text_parts.append("顶点标签:")
            for label in schema["vertex_labels"]:
                props = schema["properties"].get(label, [])
                if props:
                    text_parts.append(f"  - {label}(属性: {', '.join(props)})")
                else:
                    text_parts.append(f"  - {label}")
        
        # 边标签
        if schema["edge_labels"]:
            text_parts.append("\n边标签:")
            for label in schema["edge_labels"]:
                text_parts.append(f"  - {label}")
        
        return "\n".join(text_parts)
    
    def test_connection(self) -> bool:
        """测试数据库连接是否正常"""
        try:
            result = self.execute_gremlin("g.V().count()")
            return result["success"]
        except:
            return False


# 便捷函数：获取数据库实例
def get_db() -> HugeGraphDB:
    """获取HugeGraph数据库单例实例"""
    return HugeGraphDB()
