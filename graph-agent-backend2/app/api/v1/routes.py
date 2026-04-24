"""
API v1 路由
提供直接Gremlin查询端点
"""
from flask import request, jsonify
from .. import api_bp
from services.queries import DirectQueryService


@api_bp.route('/v1')
def api_v1():
    """API v1 测试端点"""
    return "API v1 endpoint"


@api_bp.route('/direct-query', methods=['POST'])
def handle_direct_query():
    """
    处理直接Gremlin查询请求
    
    请求体:
    {
        "gremlin": "g.V().hasLabel('Person').has('city', '北京')",
        "params": {}
    }
    
    响应:
    {
        "success": true,
        "data": [...],
        "count": 10
    }
    """
    try:
        # 1. 验证请求
        data = request.get_json()
        if not data or 'gremlin' not in data:
            return jsonify({"error": "缺少gremlin字段"}), 400
        
        gremlin_query = data['gremlin']
        params = data.get('params', None)
        
        # 2. 获取业务逻辑层服务实例（表现层不再关心数据库连接）
        query_service = DirectQueryService()
        
        # 3. 执行查询（由业务层调用基础设施层）
        result = query_service.execute(gremlin_query, params)
        
        # 4. 返回结果
        if result["success"]:
            return jsonify({
                "success": True,
                "data": result["data"],
                "count": result.get("count", 0)
            })
        else:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}"
        }), 500
