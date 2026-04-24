"""
简化版 Agent (SimpleGraphAgent) 功能测试脚本

功能：
1. 初始化 LLM 和数据库连接
2. 创建 SimpleGraphAgent 实例
3. 执行多个测试用例，验证 Agent 的基础查询能力
"""
import sys
import os
import json

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.agents.agent2 import SimpleGraphAgent
from modules.llm.client import get_llm
from modules.database.client import get_db


def test_simple_agent():
    """执行简化版 Agent 基础功能测试"""
    print("="*60)
    print("🚀 开始 SimpleGraphAgent 基础功能测试")
    print("="*60)

    try:
        # 1. 初始化组件
        print("\n📦 正在初始化组件...")
        llm = get_llm(temperature=0.5)
        db = get_db()
        
        # 2. 创建 Agent
        print("\n🤖 正在创建 SimpleGraphAgent...")
        agent = SimpleGraphAgent(llm=llm, db=db)
        
        # 3. 定义测试用例
        test_cases = [
            {
                "name": "简单计数查询",
                "question": "数据库中总共有多少个顶点？"
            },
            {
                "name": "属性过滤查询",
                "question": "找出所有在 Tech 行业工作的公司。"
            },
            {
                "name": "关系路径查询",
                "question": "Person_0 在哪个公司工作？"
            },
            {
                "name": "多跳关系查询",
                "question": "找出所有住在 City_5 的人。"
            }
        ]

        # 4. 执行测试
        results = []
        for i, case in enumerate(test_cases, 1):
            print(f"\n{'='*20} 测试用例 {i}: {case['name']} {'='*20}")
            print(f"❓ 问题: {case['question']}")
            
            result = agent.query(case['question'])
            results.append(result)
            
            # 打印简要结果
            if result["success"]:
                print(f"\n✅ 状态: 成功")
                print(f"💡 回答: {result['answer'][:300]}...")
            else:
                print(f"\n❌ 状态: 失败")
                error_msg = result.get('error', '未知错误')
                if "Arrearage" in str(error_msg):
                    print("⚠️ 提示: LLM API 账户欠费，请检查配置。")
                else:
                    print(f"⚠️ 错误: {error_msg}")

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
    test_results = test_simple_agent()
    
    # 可选：将详细结果保存到文件
    if test_results:
        output_file = os.path.join(os.path.dirname(__file__), "agent2_test_results.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n💾 详细测试结果已保存至: {output_file}")
