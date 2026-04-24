"""
Agent 功能测试脚本

功能：
1. 初始化 LLM 和数据库连接
2. 创建 GraphQueryAgent 实例
3. 执行多个测试用例，验证 Agent 的意图识别、Schema 链接、查询生成及结果解释能力
"""
import sys
import os
import json

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.agents.agent import GraphQueryAgent
from modules.llm.client import get_llm
from modules.database.client import get_db


def test_agent():
    """执行 Agent 基础功能测试"""
    print("="*60)
    print("🚀 开始 Agent 基础功能测试")
    print("="*60)

    try:
        # 1. 初始化组件
        print("\n📦 正在初始化组件...")
        llm = get_llm(temperature=0.5)
        db = get_db()
        
        # 2. 创建 Agent
        print("\n🤖 正在创建 GraphQueryAgent...")
        agent = GraphQueryAgent(llm=llm, db=db)
        print("✅ GraphQueryAgent 初始化成功")
        
        # 2.5 确保索引已创建（针对测试用例中的属性过滤）
        #agent._ensure_indexes()
        
        # 3. 定义测试用例
        test_cases = [
            {
                "name": "简单计数查询",
                "question": "数据库中总共有多少个顶点？",
                "expected_keywords": ["count", "total"]
            },
            {
                "name": "属性过滤查询",
                "question": "找出所有在 Tech 行业工作的公司。",
                "expected_keywords": ["Company", "Tech"]
            },
            {
                "name": "关系路径查询",
                "question": "Person_0 在哪个公司工作？",
                "expected_keywords": ["works_at", "Company"]
            },
            {
                "name": "多跳关系查询",
                "question": "找出所有住在 City_5 的人。",
                "expected_keywords": ["lives_in", "Person"]
            }
        ]

        # 4. 执行测试
        results = []
        for i, case in enumerate(test_cases, 1):
            print(f"\n--- 测试用例 {i}: {case['name']} ---")
            print(f"❓ 问题: {case['question']}")
            
            result = agent.process_query(case['question'])
            results.append(result)
            
            # 打印简要结果
            if result["success"]:
                print(f"✅ 状态: 成功 (重试次数: {result['retries']})")
                print(f"🔍 Gremlin: {result['gremlin']}")
                print(f"💡 解释: {result['explanation'][:100]}...")
            else:
                print(f"❌ 状态: 失败")
                print(f"⚠️ 错误: {result.get('error')}")

        # 5. 总结报告
        print("\n" + "="*60)
        print("📊 测试总结报告")
        print("="*60)
        success_count = sum(1 for r in results if r["success"])
        print(f"总用例数: {len(results)}")
        print(f"成功数量: {success_count}")
        print(f"成功率: {(success_count / len(results)) * 100:.1f}%")
        
        return results

    except Exception as e:
        print(f"\n❌ 测试过程中发生严重错误: {e}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    test_results = test_agent()
    
    # 可选：将详细结果保存到文件
    if test_results:
        output_file = os.path.join(os.path.dirname(__file__), "agent_test_results.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n💾 详细测试结果已保存至: {output_file}")
