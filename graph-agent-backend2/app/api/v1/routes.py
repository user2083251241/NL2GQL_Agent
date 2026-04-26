"""
API v1 路由
提供直接Gremlin查询端点和Agent智能查询端点
"""
from flask import request, jsonify
from .. import api_bp
from services.queries import DirectQueryService
from services.agents import get_agent_service


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


@api_bp.route('/graph-agent/query', methods=['POST'])
def handle_graph_agent_query():
    """
    处理图数据库智能Agent查询请求
    
    请求体:
    {
        "query": "用户输入的内容",
        "timestamp": 当前时间戳
    }
    
    响应:
    {
        "success": true,
        "question": "用户的问题",
        "answer": "Agent的回答",
        "timestamp": 请求时间戳
    }
    """
    try:
        # 1. 验证请求
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "error": "缺少query字段"
            }), 400
        
        user_query = data['query']
        timestamp = data.get('timestamp', None)
        
        # 2. 获取业务逻辑层服务实例（遵循分层架构原则）
        agent_service = get_agent_service()
        
        # 3. 执行业务逻辑（由业务层协调LLM和数据库）
        result = agent_service.query(user_query)
        
        # 4. 返回结果
        if result["success"]:
            response_data = {
                "success": True,
                "question": result["question"],
                "answer": result["answer"]
            }
            
            # 如果前端传了timestamp，则返回
            if timestamp is not None:
                response_data["timestamp"] = timestamp
            
            return jsonify(response_data)
        else:
            return jsonify({
                "success": False,
                "question": result["question"],
                "error": result.get("error", "未知错误")
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}"
        }), 500
