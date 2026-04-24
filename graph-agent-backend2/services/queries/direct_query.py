"""
专业查询服务 - 提供直接执行Gremlin查询的能力

职责：
1. 验证查询安全性
2. 执行参数化查询
3. 格式化结果
"""
from typing import Dict, Any, Optional
from modules.database.client import get_db
import re

# 安全配置
SAFE_PREFIXES = [
    'g.V()', 'g.E()', 'g.V().has(', 'g.E().has(', 
    'g.V().out(', 'g.V().in(', 'g.V().both(',
    'g.V().outE(', 'g.V().inE(', 'g.V().bothE(',
    'limit(', 'has(', 'where(', 'path()'
]


class DirectQueryService:
    """直接查询服务"""
    
    def __init__(self):
        # 业务层内部自行管理基础设施依赖
        self.db = get_db()
    
    def execute(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        执行安全的Gremlin查询
        
        Args:
            query: Gremlin查询语句
            params: 参数化查询的参数
            
        Returns:
            格式化的查询结果
        """
        # 1. 安全检查
        is_safe, reason = self._is_safe_query(query)
        if not is_safe:
            return {
                "success": False,
                "error": f"查询不安全: {reason}",
                "data": []
            }
        
        # 2. 参数化处理（如果需要）
        if params:
            query = self._apply_parameters(query, params)
        
        # 3. 执行查询
        return self.db.execute_gremlin(query)
    
    def _is_safe_query(self, query: str) -> tuple:
        """检查查询安全性"""
        query_lower = query.lower().strip()
        
        # 检查危险关键字
        dangerous_keywords = ['drop', 'config', 'system', 'shutdown', 'remove', 'delete']
        for keyword in dangerous_keywords:
            if keyword in query_lower:
                return False, f"包含危险关键字: {keyword}"
        
        # 检查是否以安全前缀开头
        if not any(query_lower.startswith(prefix) for prefix in SAFE_PREFIXES):
            return False, "查询必须以安全操作开头"
        
        # 额外检查：防止某些危险组合
        if re.search(r'\.drop\(\)|\.remove\(\)', query_lower):
            return False, "检测到潜在的破坏性操作"
        
        return True, ""
    
    def _apply_parameters(self, query: str, params: Dict) -> str:
        """应用参数化查询"""
        # 简单实现：替换{param}为实际值（需更安全的实现）
        for key, value in params.items():
            placeholder = f"{{{key}}}"
            if placeholder in query:
                # 安全转义
                if isinstance(value, str):
                    escaped = value.replace("'", "\\'")
                    query = query.replace(placeholder, f"'{escaped}'")
                else:
                    query = query.replace(placeholder, str(value))
        return query
