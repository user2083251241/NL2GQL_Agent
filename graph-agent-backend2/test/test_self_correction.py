"""
自我修正机制测试脚本
测试Agent的错误分析和自我修正能力
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.agents.agent_service import get_agent_service


def test_self_correction():
    """测试自我修正机制"""
    print("="*60)
    print("🚀 开始自我修正机制测试")
    print("="*60)
    
    try:
        # 获取Agent服务
        agent_service = get_agent_service()
        
        # 测试用例1：故意使用不存在的顶点标签（应该触发自我修正）
        test_cases = [
            {
                "name": "不存在的顶点标签",
                "question": "找出所有在 NonExistentCompany 工作的人"
            },
            {
                "name": "语法错误的查询",
                "question": "找出所有人的名字，但使用错误的Gremlin语法"
            }
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n{'='*20} 测试用例 {i}: {case['name']} {'='*20}")
            print(f"❓ 问题: {case['question']}")
            
            result = agent_service.query(case['question'])
            
            if result["success"]:
                print(f"\n✅ 状态: 成功")
                print(f"💡 回答: {result['answer'][:300]}...")
            else:
                print(f"\n❌ 状态: 失败")
                error_msg = result.get('error', '未知错误')
                print(f"⚠️ 错误: {error_msg}")
                
                # 检查是否包含自我修正的迹象
                if "analyze_and_correct_error" in error_msg or "修正" in error_msg:
                    print("🔍 检测到自我修正尝试")
        
        print("\n" + "="*60)
        print("📊 自我修正测试完成")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_self_correction()