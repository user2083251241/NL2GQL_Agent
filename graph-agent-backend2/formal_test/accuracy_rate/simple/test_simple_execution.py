# -*- coding: utf-8 -*-
"""
Agent Gremlin 执行准确率测试脚本（Simple级别）- SSE版本

功能：
1. 从 ground_truth_answers.json 提取 simple 级别的测试用例
2. 通过 HTTP POST 请求调用 Agent SSE 流式接口
3. 解析 SSE 响应，提取 final_answer 事件中的 JSON 数据
4. 从 "gremlin语句" 字段提取 Gremlin 查询
5. 执行该 Gremlin 查询，验证是否能成功执行
6. 统计执行通过率

使用方法：
python formal_test/accuracy_rate/test_agent_gremlin_execution_sse.py
"""

import sys
import os
import json
import re
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests

# 添加项目根目录到 Python 路径
# 当前文件: formal_test/accuracy_rate/simple/test_simple_execution.py
# 需要向上4层到达项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"✅ 已添加项目根目录到 Python 路径: {project_root}")
else:
    print(f"ℹ️  项目根目录已在 Python 路径中: {project_root}")

from modules.database.client import get_db


# SSE 接口配置
SSE_API_URL = "http://localhost:5000/api/graph-agent/query/stream"


def load_simple_test_cases(file_path: str) -> List[Dict[str, Any]]:
    """加载 simple 级别的测试用例"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            all_test_cases = json.load(f)
        
        # 只筛选 simple 级别的测试用例
        simple_cases = [tc for tc in all_test_cases if tc.get("level") == "simple"]
        print(f"✅ 成功加载 {len(simple_cases)} 个 simple 级别测试用例（总共 {len(all_test_cases)} 个）")
        return simple_cases
    except Exception as e:
        print(f"❌ 加载测试用例失败: {e}")
        sys.exit(1)


def extract_gremlin_from_final_answer(final_answer: str) -> Optional[str]:
    """
    从 final_answer 内容中提取 Gremlin 语句
    
    Args:
        final_answer: final_answer 事件的 content 字段
        
    Returns:
        提取到的 Gremlin 语句，如果提取失败返回 None
    """
    try:
        # 策略0: 检查是否为纯 Gremlin 查询（以 g. 开头）
        stripped = final_answer.strip()
        if stripped.startswith('g.') or stripped.startswith('G.'):
            # 直接返回整个内容作为 Gremlin 查询
            return stripped
        
        # 策略1: 尝试直接解析整个 final_answer 为 JSON（最可靠）
        try:
            data = json.loads(final_answer)
            # 支持多种字段名变体（大小写兼容）
            gremlin = (data.get("Gremlin语句") or 
                      data.get("gremlin语句") or 
                      data.get("gremlin") or
                      data.get("Gremlin"))
            if gremlin and isinstance(gremlin, str):
                return gremlin
        except json.JSONDecodeError:
            pass
        
        # 策略2: 查找 Final Answer: {...} 格式，使用贪婪匹配
        pattern = r'Final Answer:\s*(\{.*\})'
        match = re.search(pattern, final_answer, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            try:
                # 尝试解析提取到的 JSON
                data = json.loads(json_str)
                # 支持多种字段名变体（大小写兼容）
                gremlin = (data.get("Gremlin语句") or 
                          data.get("gremlin语句") or 
                          data.get("gremlin") or
                          data.get("Gremlin"))
                if gremlin and isinstance(gremlin, str):
                    return gremlin
            except json.JSONDecodeError:
                # 如果解析失败，可能是截断的JSON，尝试修复
                pass
        
        # 策略3: 查找任何包含 "gremlin语句" 的 JSON 片段
        # 使用更宽松的模式匹配
        pattern_loose = r'\{[^{}]*"gremlin语句"\s*:\s*"([^"]+)"[^{}]*\}'
        matches = re.findall(pattern_loose, final_answer, re.DOTALL)
        
        if matches:
            # 返回第一个匹配的结果
            return matches[0]
        
        # 策略4: 使用 ast.literal_eval 处理 Python 风格的字典（支持单引号）
        if '"gremlin语句"' in final_answer or 'gremlin语句' in final_answer:
            import ast
            try:
                # 查找最外层的字典结构
                start_idx = final_answer.find('{')
                end_idx = final_answer.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    dict_str = final_answer[start_idx:end_idx+1]
                    # 尝试使用 ast.literal_eval 解析（支持 Python 字面量）
                    data = ast.literal_eval(dict_str)
                    if isinstance(data, dict):
                        gremlin = data.get("gremlin语句", None)
                        if gremlin:
                            return gremlin
            except (ValueError, SyntaxError):
                # ast.literal_eval 失败，尝试其他方法
                pass
        
        # 策略5: 手动提取 gremlin语句 字段的值
        # 匹配 "gremlin语句": "..." 或 'gremlin语句': '...'
        patterns = [
            r'"gremlin语句"\s*:\s*"((?:[^"\\]|\\.)*)"',  # 双引号键和值
            r"'gremlin语句'\s*:\s*'((?:[^'\\]|\\.)*)'",  # 单引号键和值
            r'"gremlin语句"\s*:\s*\'((?:[^\'\\]|\\.)*)\'',  # 双引号键，单引号值
            r"'gremlin语句'\s*:\s*\"((?:[^\"\\]|\\.)*)\"",  # 单引号键，双引号值
        ]
        
        for pattern in patterns:
            match = re.search(pattern, final_answer, re.DOTALL)
            if match:
                gremlin = match.group(1)
                # 处理转义字符
                gremlin = gremlin.replace('\\"', '"').replace("\\'", "'")
                return gremlin
        
        # 策略6: 检测是否包含典型的 Gremlin 关键词（兜底方案）
        gremlin_keywords = ['g.V()', 'g.E()', '.has(', '.outE(', '.inE(', '.values(', '.count(', '.limit(']
        if any(keyword in final_answer for keyword in gremlin_keywords):
            # 假设整个内容就是 Gremlin 查询
            return stripped
        
        return None
    except Exception as e:
        print(f"⚠️  提取 Gremlin 语句失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def call_agent_sse_api(question: str) -> Dict[str, Any]:
    """
    调用 Agent SSE 流式接口
    
    Args:
        question: 自然语言问题
        
    Returns:
        {
            "success": bool,
            "final_answer": str,
            "error": str (可选),
            "steps": list (所有推理步骤),
            "execution_time": float (执行时间，秒),
            "token_usage": dict (可选，token使用统计)
        }
    """
    try:
        # 准备请求数据
        payload = {
            "query": question,
            "timestamp": int(time.time()),
            "enable_self_correction": True
        }
        
        # 记录开始时间
        start_time = time.time()
        
        # 发送 POST 请求，启用流式响应
        response = requests.post(
            SSE_API_URL,
            json=payload,
            stream=True,
            timeout=120  # 设置较长的超时时间
        )
        
        if response.status_code != 200:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "final_answer": None,
                "error": f"HTTP {response.status_code}: {response.text}",
                "steps": [],
                "execution_time": execution_time,
                "token_usage": None
            }
        
        # 解析 SSE 流
        steps = []
        final_answer = None
        has_final_response = False
        token_usage = None  # 初始化 token_usage 变量
        
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                
                # 解析 SSE 格式: data: {...}
                if decoded_line.startswith('data: '):
                    try:
                        data = json.loads(decoded_line[6:])
                        event_type = data.get('type', '')
                        content = data.get('content', '')
                        
                        # 调试：打印事件类型和内容
                        if event_type in ['final_answer', 'error'] or 'answer' in data:
                            print(f"    [DEBUG] 收到事件: type={event_type}")
                            if event_type == 'error':
                                print(f"    [DEBUG] 错误内容: {content[:200]}")
                        
                        # 记录所有步骤
                        steps.append({
                            "type": event_type,
                            "content": content,
                            "timestamp": data.get('timestamp')
                        })
                        
                        # 捕获 final_answer 类型的事件
                        if event_type == 'final_answer':
                            final_answer = content
                            # 从 final_answer 事件中提取 token_usage（如果存在）
                            if 'token_usage' in data:
                                token_usage = data.get('token_usage')
                        
                        # 检查是否收到最终答案事件（包含完整响应结构）
                        if 'answer' in data and 'success' in data:
                            has_final_response = True
                            if data['success']:
                                final_answer = data['answer']
                                # 提取token使用信息（如果有）
                                token_usage = data.get('token_usage', None)
                            else:
                                execution_time = time.time() - start_time
                                return {
                                    "success": False,
                                    "final_answer": None,
                                    "error": data.get('error', '未知错误'),
                                    "steps": steps,
                                    "execution_time": execution_time,
                                    "token_usage": None
                                }
                                
                    except json.JSONDecodeError as e:
                        print(f"⚠️  JSON 解析失败: {e}")
                        continue
        
        # 计算执行时间
        execution_time = time.time() - start_time
        
        # 如果收到了最终响应，返回成功
        if has_final_response and final_answer:
            return {
                "success": True,
                "final_answer": final_answer,
                "steps": steps,
                "execution_time": execution_time,
                "token_usage": token_usage
            }
        # 如果没有收到最终响应但有 final_answer 内容
        elif final_answer:
            return {
                "success": True,
                "final_answer": final_answer,
                "steps": steps,
                "execution_time": execution_time,
                "token_usage": token_usage
            }
        else:
            return {
                "success": False,
                "final_answer": None,
                "error": "未收到 final_answer",
                "steps": steps,
                "execution_time": execution_time,
                "token_usage": None
            }
            
    except requests.exceptions.Timeout:
        execution_time = time.time() - start_time
        return {
            "success": False,
            "final_answer": None,
            "error": "请求超时",
            "steps": [],
            "execution_time": execution_time,
            "token_usage": None
        }
    except requests.exceptions.ConnectionError:
        execution_time = time.time() - start_time
        return {
            "success": False,
            "final_answer": None,
            "error": "连接失败，请确认后端服务正在运行",
            "steps": [],
            "execution_time": execution_time,
            "token_usage": None
        }
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            "success": False,
            "final_answer": None,
            "error": str(e),
            "steps": [],
            "execution_time": execution_time,
            "token_usage": None
        }


def execute_gremlin_query(db, query: str) -> Dict[str, Any]:
    """执行单个 Gremlin 查询并返回结果"""
    try:
        result = db.execute_gremlin(query)
        return {
            "success": result.get("success", False),
            "data": result.get("data", []),
            "count": result.get("count", 0),
            "error": result.get("error", None)
        }
    except Exception as e:
        return {
            "success": False,
            "data": [],
            "count": 0,
            "error": str(e)
        }


def test_agent_gremlin_execution(test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    通过 SSE 接口批量测试 Agent Gremlin 查询的执行
    
    Args:
        test_cases: 测试用例列表
        
    Returns:
        测试结果统计字典
    """
    db = get_db()
    
    results = {
        "total": len(test_cases),
        "success_count": 0,
        "failed_count": 0,
        "extraction_failed_count": 0,
        "api_call_failed_count": 0,
        "execution_success_rate": 0.0,
        "test_results": [],
        "generated_at": datetime.now().isoformat(),
        # 新增：时间统计相关字段
        "execution_times": [],  # 所有成功用例的执行时间列表
        "avg_execution_time": 0.0,  # 平均执行时间
        "min_execution_time": 0.0,  # 最小执行时间
        "max_execution_time": 0.0,  # 最大执行时间
        "total_execution_time": 0.0,  # 总执行时间
        # 新增：Token使用统计相关字段
        "token_usages": [],  # 所有成功用例的token使用列表
        "total_prompt_tokens": 0,  # 总prompt token数
        "total_completion_tokens": 0,  # 总completion token数
        "total_tokens": 0,  # 总token数
        "avg_tokens_per_query": 0.0,  # 平均每次查询的token数
        "estimated_total_cost_usd": 0.0  # 预估总成本（美元）
    }
    
    print("\n" + "="*80)
    print("开始执行 Agent Gremlin 查询测试（Simple 级别 - SSE 版本）")
    print("="*80 + "\n")
    
    for i, test_case in enumerate(test_cases, 1):
        case_id = test_case.get("id", i)
        question = test_case.get("question", "N/A")
        expected_gremlin = test_case.get("gremlin_query", "")
        
        print(f"[{i}/{len(test_cases)}] 测试用例 #{case_id}")
        print(f"  问题: {question}")
        print(f"  预期 Gremlin: {expected_gremlin[:80]}{'...' if len(expected_gremlin) > 80 else ''}")
        
        # Step 1: 调用 Agent SSE 接口
        print(f"  🌐 调用 Agent SSE 接口...")
        api_result = call_agent_sse_api(question)
        
        # 记录执行时间
        execution_time = api_result.get("execution_time", 0.0)
        print(f"  ⏱️  执行时间: {execution_time:.2f} 秒")
        
        # 提取token使用信息
        token_usage = api_result.get("token_usage", None)
        if token_usage:
            print(f"  📊 Token使用: {token_usage['total_tokens']} (prompt={token_usage['prompt_tokens']}, completion={token_usage['completion_tokens']})")
        
        if not api_result.get("success"):
            print(f"  ❌ API 调用失败: {api_result.get('error', 'Unknown error')}")
            test_result = {
                "id": case_id,
                "question": question,
                "expected_gremlin": expected_gremlin,
                "api_success": False,
                "api_error": api_result.get("error"),
                "final_answer": None,
                "extracted_gremlin": None,
                "extraction_success": False,
                "execution_success": False,
                "execution_error": "API调用失败",
                "execution_time": execution_time,
                "token_usage": token_usage
            }
            results["test_results"].append(test_result)
            results["failed_count"] += 1
            results["api_call_failed_count"] += 1
            print()
            continue
        
        print(f"  ✅ API 调用成功 (收到 {len(api_result.get('steps', []))} 个步骤)")
        
        # Step 2: 从 final_answer 中提取 Gremlin 语句
        final_answer = api_result.get("final_answer", "")
        print(f"  🔍 提取 Gremlin 语句...")
        extracted_gremlin = extract_gremlin_from_final_answer(final_answer)
        
        # 二次提取检查：确保提取的是纯Gremlin语句而非JSON对象
        if extracted_gremlin:
            # 检查是否为纯Gremlin语句
            is_pure_gremlin = extracted_gremlin.strip().startswith('g.') or extracted_gremlin.strip().startswith('G.')
            
            if not is_pure_gremlin:
                # 尝试方法1: 解析为JSON
                try:
                    parsed_data = json.loads(extracted_gremlin)
                    if isinstance(parsed_data, dict):
                        gremlin_value = parsed_data.get("Gremlin语句") or parsed_data.get("gremlin语句") or parsed_data.get("gremlin")
                        if gremlin_value and isinstance(gremlin_value, str):
                            extracted_gremlin = gremlin_value.strip()
                            print(f"  ✅ 二次提取(方法1-JSON解析): {extracted_gremlin[:80]}{'...' if len(extracted_gremlin) > 80 else ''}")
                except (json.JSONDecodeError, ValueError):
                    pass
            
            # 如果仍然不是纯Gremlin语句，尝试方法2: 正则提取
            if extracted_gremlin and not (extracted_gremlin.strip().startswith('g.') or extracted_gremlin.strip().startswith('G.')):
                # 使用正则从字符串中提取 Gremlin语句 字段
                patterns = [
                    r'"Gremlin语句"\s*:\s*"([^"]+)"',
                    r'"gremlin语句"\s*:\s*"([^"]+)"',
                    r"'Gremlin语句'\s*:\s*'([^']+)'",
                    r"'gremlin语句'\s*:\s*'([^']+)'",
                ]
                for pattern in patterns:
                    match = re.search(pattern, extracted_gremlin)
                    if match:
                        extracted_gremlin = match.group(1).strip()
                        print(f"  ✅ 二次提取(方法2-正则): {extracted_gremlin[:80]}{'...' if len(extracted_gremlin) > 80 else ''}")
                        break
            
            # 最终验证：确保提取到的是纯Gremlin语句
            if extracted_gremlin and not (extracted_gremlin.strip().startswith('g.') or extracted_gremlin.strip().startswith('G.')):
                print(f"  ⚠️  提取结果不是纯Gremlin语句: {extracted_gremlin[:100]}...")
                extracted_gremlin = None
        
        if not extracted_gremlin:
            print(f"  ⚠️  无法从 final_answer 中提取 Gremlin 语句")
            print(f"     final_answer: {final_answer[:200]}{'...' if len(final_answer) > 200 else ''}")
            test_result = {
                "id": case_id,
                "question": question,
                "expected_gremlin": expected_gremlin,
                "api_success": True,
                "final_answer": final_answer[:500],  # 保存部分答案用于调试
                "extracted_gremlin": None,
                "extraction_success": False,
                "execution_success": False,
                "execution_error": "提取失败",
                "execution_time": execution_time,
                "token_usage": token_usage
            }
            results["test_results"].append(test_result)
            results["failed_count"] += 1
            results["extraction_failed_count"] += 1
            print()
            continue
        
        print(f"  ✅ 提取成功: {extracted_gremlin[:80]}{'...' if len(extracted_gremlin) > 80 else ''}")
        
        # Step 3: 执行提取的 Gremlin 查询
        print(f"  🗄️  执行 Gremlin 查询...")
        exec_result = execute_gremlin_query(db, extracted_gremlin)
        
        # 记录结果
        test_result = {
            "id": case_id,
            "question": question,
            "expected_gremlin": expected_gremlin,
            "api_success": True,
            "final_answer": final_answer[:500],
            "extracted_gremlin": extracted_gremlin,
            "extraction_success": True,
            "execution_success": exec_result["success"],
            "execution_error": exec_result["error"],
            "result_count": exec_result["count"],
            "execution_time": execution_time,  # 添加执行时间
            "token_usage": token_usage  # 添加token使用信息
        }
        
        results["test_results"].append(test_result)
        
        if exec_result["success"]:
            results["success_count"] += 1
            results["execution_times"].append(execution_time)  # 记录成功的执行时间
            
            # 记录token使用信息
            if token_usage:
                results["token_usages"].append(token_usage)
                results["total_prompt_tokens"] += token_usage.get("prompt_tokens", 0)
                results["total_completion_tokens"] += token_usage.get("completion_tokens", 0)
                results["total_tokens"] += token_usage.get("total_tokens", 0)
                results["estimated_total_cost_usd"] += token_usage.get("estimated_cost_usd", 0.0)
            
            print(f"  ✅ 执行成功 (返回 {exec_result['count']} 条结果)")
        else:
            results["failed_count"] += 1
            print(f"  ❌ 执行失败: {exec_result['error'][:150]}")
        
        print()
    
    # 计算执行成功率
    if results["total"] > 0:
        results["execution_success_rate"] = (results["success_count"] / results["total"]) * 100
    
    # 计算时间统计
    if results["execution_times"]:
        results["total_execution_time"] = sum(results["execution_times"])
        results["avg_execution_time"] = results["total_execution_time"] / len(results["execution_times"])
        results["min_execution_time"] = min(results["execution_times"])
        results["max_execution_time"] = max(results["execution_times"])
    
    # 计算token统计
    if results["token_usages"]:
        results["avg_tokens_per_query"] = results["total_tokens"] / len(results["token_usages"])
    
    return results


def generate_report(results: Dict[str, Any], output_dir: str):
    """生成测试报告"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成 JSON 报告
    json_report_path = os.path.join(output_dir, "agent_gremlin_execution_results_simple_sse.json")
    with open(json_report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"📄 JSON 报告已保存: {json_report_path}")
    
    # 生成文本摘要报告
    txt_report_path = os.path.join(output_dir, "summary_simple3.txt")
    with open(txt_report_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("Agent Gremlin 查询执行准确率测试报告（Simple 级别 - SSE 版本）\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"测试时间: {results['generated_at']}\n")
        f.write(f"SSE 接口地址: {SSE_API_URL}\n")
        f.write(f"测试总数: {results['total']}\n")
        f.write(f"执行成功数量: {results['success_count']}\n")
        f.write(f"执行失败数量: {results['failed_count']}\n")
        f.write(f"提取失败数量: {results['extraction_failed_count']}\n")
        f.write(f"API调用失败数量: {results['api_call_failed_count']}\n")
        f.write(f"执行通过率: {results['execution_success_rate']:.2f}%\n\n")
        
        # 新增：时间统计信息
        if results["execution_times"]:
            f.write("-"*80 + "\n")
            f.write("LLM 执行时间统计:\n")
            f.write("-"*80 + "\n")
            f.write(f"总执行时间: {results['total_execution_time']:.2f} 秒\n")
            f.write(f"平均执行时间: {results['avg_execution_time']:.2f} 秒\n")
            f.write(f"最小执行时间: {results['min_execution_time']:.2f} 秒\n")
            f.write(f"最大执行时间: {results['max_execution_time']:.2f} 秒\n")
            f.write(f"有效样本数: {len(results['execution_times'])}\n\n")
        
        # 新增：Token使用统计信息
        if results["token_usages"]:
            f.write("-"*80 + "\n")
            f.write("LLM Token 使用统计:\n")
            f.write("-"*80 + "\n")
            f.write(f"总 Prompt Tokens: {results['total_prompt_tokens']}\n")
            f.write(f"总 Completion Tokens: {results['total_completion_tokens']}\n")
            f.write(f"总 Token 数: {results['total_tokens']}\n")
            f.write(f"平均每次查询 Token 数: {results['avg_tokens_per_query']:.0f}\n")
            f.write(f"预估总成本 (USD): ${results['estimated_total_cost_usd']:.4f}\n")
            f.write(f"有效样本数: {len(results['token_usages'])}\n\n")

        # 失败的查询详情
        failed_tests = [t for t in results["test_results"] if not t["execution_success"]]
        if failed_tests:
            f.write("-"*80 + "\n")
            f.write("失败的查询详情:\n")
            f.write("-"*80 + "\n\n")
            
            for test in failed_tests:
                f.write(f"ID: {test['id']}\n")
                f.write(f"问题: {test['question']}\n")
                f.write(f"预期 Gremlin: {test['expected_gremlin']}\n")
                
                if test.get('execution_time'):
                    f.write(f"执行时间: {test['execution_time']:.2f} 秒\n")
                
                if not test.get("api_success"):
                    f.write(f"API 状态: 失败\n")
                    f.write(f"失败原因: {test.get('execution_error', '未知')}\n")
                elif not test.get("extraction_success"):
                    f.write(f"提取状态: 失败\n")
                    f.write(f"失败原因: {test.get('execution_error', '未知')}\n")
                    if test.get("final_answer"):
                        f.write(f"final_answer: {test['final_answer']}\n")
                else:
                    f.write(f"提取 Gremlin: {test['extracted_gremlin']}\n")
                    f.write(f"执行错误: {test['execution_error']}\n")
                
                f.write("\n" + "-"*40 + "\n\n")
        
        # 成功的查询列表
        success_tests = [t for t in results["test_results"] if t["execution_success"]]
        if success_tests:
            f.write("-"*80 + "\n")
            f.write("成功的查询列表:\n")
            f.write("-"*80 + "\n\n")
            
            for test in success_tests:
                f.write(f"✓ ID {test['id']}: {test['question']}\n")
                f.write(f"  预期: {test['expected_gremlin']}\n")
                f.write(f"  提取: {test['extracted_gremlin']}\n")
                f.write(f"  结果数: {test['result_count']}\n")
                if test.get('execution_time'):
                    f.write(f"  执行时间: {test['execution_time']:.2f} 秒\n")
                f.write("\n")
    
    print(f"📄 文本报告已保存: {txt_report_path}")


def main():
    """主函数"""
    print("="*80)
    print("Agent Gremlin 查询执行准确率测试（Simple 级别 - SSE 版本）")
    print("="*80)
    
    # 检查后端服务是否运行
    print("\n🔍 检查后端服务状态...")
    try:
        health_response = requests.get("http://localhost:5000/api/v1", timeout=5)
        if health_response.status_code == 200:
            print("✅ 后端服务正常运行")
        else:
            print(f"⚠️  后端服务返回异常状态码: {health_response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请先启动后端:")
        print("   python run.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 检查后端服务失败: {e}")
        sys.exit(1)
    
    # 加载测试用例
    ground_truth_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "ground_truth_answers.json"
    )
    
    if not os.path.exists(ground_truth_file):
        print(f"❌ 文件不存在: {ground_truth_file}")
        print("请先运行 generate_ground_truth.py 生成测试数据")
        sys.exit(1)
    
    test_cases = load_simple_test_cases(ground_truth_file)
    
    if not test_cases:
        print("❌ 没有可用的 simple 级别测试用例")
        sys.exit(1)
    
    # 执行测试
    results = test_agent_gremlin_execution(test_cases)
    
    # 生成报告
    output_dir = os.path.dirname(os.path.abspath(__file__))
    generate_report(results, output_dir)
    
    # 打印总结
    print("\n" + "="*80)
    print("测试完成总结")
    print("="*80)
    print(f"总测试数: {results['total']}")
    print(f"执行成功: {results['success_count']}")
    print(f"执行失败: {results['failed_count']}")
    print(f"提取失败: {results['extraction_failed_count']}")
    print(f"API调用失败: {results['api_call_failed_count']}")
    print(f"执行通过率: {results['execution_success_rate']:.2f}%")
    
    # 新增：打印时间统计
    if results["execution_times"]:
        print("\n⏱️  LLM 执行时间统计:")
        print(f"  总执行时间: {results['total_execution_time']:.2f} 秒")
        print(f"  平均执行时间: {results['avg_execution_time']:.2f} 秒")
        print(f"  最小执行时间: {results['min_execution_time']:.2f} 秒")
        print(f"  最大执行时间: {results['max_execution_time']:.2f} 秒")
        print(f"  有效样本数: {len(results['execution_times'])}")
    
    # 新增：打印Token使用统计
    if results["token_usages"]:
        print("\n📊 LLM Token 使用统计:")
        print(f"  总 Prompt Tokens: {results['total_prompt_tokens']}")
        print(f"  总 Completion Tokens: {results['total_completion_tokens']}")
        print(f"  总 Token 数: {results['total_tokens']}")
        print(f"  平均每次查询 Token 数: {results['avg_tokens_per_query']:.0f}")
        print(f"  预估总成本 (USD): ${results['estimated_total_cost_usd']:.4f}")
        print(f"  有效样本数: {len(results['token_usages'])}")

    if results['execution_success_rate'] == 100.0:
        print("🎉 所有 Agent 生成的 Gremlin 查询均能成功执行！")
    elif results['execution_success_rate'] >= 80.0:
        print("⚠️  大部分查询可以执行，但存在部分失败的查询需要检查")
    else:
        print("❌ 大量查询执行失败，请检查 Agent 的 Gremlin 生成能力")
    
    print("\n详细报告已保存到 accuracy_rate 目录")


if __name__ == "__main__":
    main()