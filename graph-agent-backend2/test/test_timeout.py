"""
测试AgentExecutor的超时功能
验证max_execution_time参数是否正常工作
"""
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.agents.agent2 import GraphAgent
from modules.llm.client import get_llm
from modules.database.client import HugeGraphDB


def test_timeout_functionality():
    """
    测试超时功能
    使用查询："找出评分为5的喜剧电影有哪些"
    """
    print("=" * 80)
    print("测试AgentExecutor超时功能")
    print("=" * 80)
    
    # 初始化组件
    print("\n1. 初始化LLM和数据库连接...")
    llm = get_llm()
    db = HugeGraphDB()
    
    # 创建Agent（设置较短的超时时间以便测试）
    print("\n2. 创建GraphAgent（设置超时时间为30秒）...")
    agent = GraphAgent(llm=llm, db=db, enable_self_correction=True)
    
    # 修改超时时间为30秒用于测试
    agent.agent_executor.max_execution_time = 30.0
    agent.agent_executor.max_iterations = 10  # 允许较多迭代次数
    
    print(f"   - max_execution_time: {agent.agent_executor.max_execution_time}秒")
    print(f"   - max_iterations: {agent.agent_executor.max_iterations}")
    
    # 执行测试查询
    test_question = "找出评分为5的喜剧电影有哪些"
    print(f"\n3. 执行测试查询: '{test_question}'")
    print("-" * 80)
    
    start_time = time.time()
    
    try:
        result = agent.query(test_question)
        elapsed_time = time.time() - start_time
        
        print("-" * 80)
        print(f"\n✅ 查询完成!")
        print(f"   - 耗时: {elapsed_time:.2f}秒")
        print(f"   - 成功: {result['success']}")
        
        if result['success']:
            print(f"\n📊 答案:")
            print(f"   {result['answer'][:500]}{'...' if len(result['answer']) > 500 else ''}")
            
            # 检查是否在超时限制内完成
            if elapsed_time <= agent.agent_executor.max_execution_time:
                print(f"\n✅ 超时控制正常: 在{agent.agent_executor.max_execution_time}秒内完成")
            else:
                print(f"\n⚠️ 警告: 执行时间({elapsed_time:.2f}秒)超过了设定的超时时间({agent.agent_executor.max_execution_time}秒)")
        else:
            print(f"\n❌ 查询失败:")
            print(f"   错误: {result.get('error', '未知错误')}")
            
    except Exception as e:
        elapsed_time = time.time() - start_time
        print("-" * 80)
        print(f"\n❌ 发生异常:")
        print(f"   - 耗时: {elapsed_time:.2f}秒")
        print(f"   - 错误类型: {type(e).__name__}")
        print(f"   - 错误信息: {str(e)}")
        
        # 检查是否是超时异常
        if "timeout" in str(e).lower() or "time limit" in str(e).lower():
            print(f"\n✅ 超时机制触发: 查询被正确终止")
        else:
            print(f"\n⚠️ 非超时异常")
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
    
    return result


def test_with_different_timeouts():
    """
    测试不同的超时设置
    """
    print("\n\n" + "=" * 80)
    print("测试不同超时设置的影响")
    print("=" * 80)
    
    llm = get_llm()
    db = HugeGraphDB()
    
    timeouts = [15.0, 30.0, 60.0]
    test_question = "找出评分为5的喜剧电影有哪些"
    
    for timeout in timeouts:
        print(f"\n{'='*60}")
        print(f"测试超时设置: {timeout}秒")
        print(f"{'='*60}")
        
        agent = GraphAgent(llm=llm, db=db, enable_self_correction=True)
        agent.agent_executor.max_execution_time = timeout
        agent.agent_executor.max_iterations = 10
        
        start_time = time.time()
        try:
            result = agent.query(test_question)
            elapsed_time = time.time() - start_time
            
            print(f"结果: {'成功' if result['success'] else '失败'}")
            print(f"耗时: {elapsed_time:.2f}秒")
            
            if elapsed_time < timeout:
                print(f"状态: ✅ 在超时限制内完成")
            else:
                print(f"状态: ⚠️ 达到或超过超时限制")
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"异常: {type(e).__name__}: {str(e)[:100]}")
            print(f"耗时: {elapsed_time:.2f}秒")
        
        # 等待一下避免请求过于频繁
        time.sleep(2)


if __name__ == "__main__":
    # 运行基本超时测试
    result = test_timeout_functionality()
    
    # 可选：运行不同超时设置的对比测试
    # test_with_different_timeouts()
    
    print("\n\n提示: 如需测试不同超时设置，请取消注释 test_with_different_timeouts() 调用")
