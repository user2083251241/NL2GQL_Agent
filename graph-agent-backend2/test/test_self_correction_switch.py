"""
自我修正开关功能测试脚本
测试启用和禁用自我修正功能的行为差异
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.agents.agent_service import AgentQueryService


def test_self_correction_enabled():
    """测试启用自我修正功能"""
    print("="*60)
    print("🚀 测试启用自我修正功能")
    print("="*60)
    
    # 重置服务以确保干净状态
    AgentQueryService.reset()
    
    # 创建启用自我修正的服务实例
    service = AgentQueryService(enable_self_correction=True)
    
    print(f"✅ 服务初始化完成，自我修正: 启用")
    print(f"🔧 工具列表: {[tool.name for tool in service._agent.tools]}")
    
    return service


def test_self_correction_disabled():
    """测试禁用自我修正功能"""
    print("="*60)
    print("🚀 测试禁用自我修正功能")
    print("="*60)
    
    # 重置服务以确保干净状态
    AgentQueryService.reset()
    
    # 创建禁用自我修正的服务实例
    service = AgentQueryService(enable_self_correction=False)
    
    print(f"✅ 服务初始化完成，自我修正: 禁用")
    print(f"🔧 工具列表: {[tool.name for tool in service._agent.tools]}")
    
    return service


def main():
    """主测试函数"""
    try:
        # 测试启用自我修正
        enabled_service = test_self_correction_enabled()
        
        print("\n" + "-"*60)
        
        # 测试禁用自我修正
        disabled_service = test_self_correction_disabled()
        
        print("\n" + "="*60)
        print("📊 自我修正开关功能测试完成")
        print("="*60)
        
        # 验证工具列表差异
        enabled_tools = [tool.name for tool in enabled_service._agent.tools]
        disabled_tools = [tool.name for tool in disabled_service._agent.tools]
        
        print(f"\n✅ 启用模式工具: {enabled_tools}")
        print(f"✅ 禁用模式工具: {disabled_tools}")
        
        if "analyze_and_correct_error" in enabled_tools and "analyze_and_correct_error" not in disabled_tools:
            print("✅ 自我修正开关功能正常工作！")
        else:
            print("❌ 自我修正开关功能存在问题！")
            
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()