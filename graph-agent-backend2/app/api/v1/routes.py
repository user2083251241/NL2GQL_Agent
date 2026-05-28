"""
API v1 路由
提供直接Gremlin查询端点和Agent智能查询端点
"""
from flask import request, jsonify, Response
import json
import time
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
        "timestamp": 当前时间戳,
        "enable_self_correction": true/false (可选，默认为true)
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
        enable_self_correction = data.get('enable_self_correction', True)  # ！！！！此为启动开关，默认启用
        
        # 2. 获取业务逻辑层服务实例（遵循分层架构原则）
        # 注意：由于是单例模式，第一次调用的参数会生效
        # 在实际生产环境中，可能需要考虑每个请求独立的Agent实例
        agent_service = get_agent_service(enable_self_correction=enable_self_correction)
        
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
            
            # 添加token使用统计
            if "token_usage" in result:
                response_data["token_usage"] = result["token_usage"]
            
            return jsonify(response_data)
        else:
            response_data = {
                "success": False,
                "question": result["question"],
                "error": result.get("error", "未知错误")
            }
            
            # 添加token使用统计（即使失败也返回）
            if "token_usage" in result:
                response_data["token_usage"] = result["token_usage"]
            
            return jsonify(response_data), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}"
        }), 500


@api_bp.route('/graph-agent/query/stream', methods=['POST'])
def handle_graph_agent_query_stream():
    """
    处理图数据库智能Agent流式查询请求（SSE）
    
    请求体:
    {
        "query": "用户输入的内容",
        "timestamp": 当前时间戳,
        "enable_self_correction": true/false (可选，默认为true)
    }
    
    响应:
    SSE事件流，每个事件格式:
    data: {"type": "thought|action|observation|final_answer|error", "content": "...", "timestamp": 123}
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
        enable_self_correction = data.get('enable_self_correction', True)
        
        # 2. 获取业务逻辑层服务实例
        agent_service = get_agent_service(enable_self_correction=enable_self_correction)
        
        # 3. 创建SSE响应生成器
        def generate():
            try:
                final_answer = None
                token_usage = None
                
                # 执行流式查询
                for event in agent_service.stream_query(user_query):
                    # 将事件转换为SSE格式
                    sse_data = json.dumps(event, ensure_ascii=False)
                    yield f"data: {sse_data}\n\n"
                    
                    # 捕获最终答案和token使用信息
                    if event.get('type') == 'final_answer':
                        final_answer = event.get('content', '')
                        # 提取token使用信息（如果存在）
                        token_usage = event.get('token_usage', None)
                    
                    # 强制刷新缓冲区
                    time.sleep(0.01)
                
                # 流式推理结束后，发送最终答案（与非流式接口格式一致）
                if final_answer:
                    final_event = {
                        "success": True,
                        "question": user_query,
                        "answer": final_answer,
                        "timestamp": timestamp or int(time.time())
                    }
                    # 添加token使用统计
                    if token_usage:
                        final_event["token_usage"] = token_usage
                    yield f"data: {json.dumps(final_event, ensure_ascii=False)}\n\n"
                    
            except GeneratorExit:
                # 客户端断开连接
                print("⚠️ 客户端断开SSE连接")
            except Exception as e:
                error_event = {
                    "type": "error",
                    "content": f"流式查询失败: {str(e)}",
                    "timestamp": int(time.time())
                }
                yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"

        # 4. 返回SSE响应
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',  # 禁用Nginx缓冲
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }
        )
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}"
        }), 500