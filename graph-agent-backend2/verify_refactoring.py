"""
重构验证脚本 - 测试新的导入路径是否正常工作
"""
import sys

def test_imports():
    """测试所有关键导入"""
    print("=" * 60)
    print("🧪 重构验证 - 导入测试")
    print("=" * 60)
    
    tests = [
        ("基础设施层 - Database", "from modules.database.client import HugeGraphDB, get_db"),
        ("基础设施层 - LLM", "from modules.llm.client import create_llm, get_llm"),
        ("业务层 - Agent", "from services.agents.agent import GraphQueryAgent"),
        ("业务层 - DirectQuery", "from services.queries.direct_query import DirectQueryService"),
        ("向后兼容 - Database", "from modules.database import HugeGraphDB as OldHugeGraphDB"),
        ("向后兼容 - LLM", "from modules.llm import get_llm as old_get_llm"),
    ]
    
    passed = 0
    failed = 0
    
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✅ {name}: 成功")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: 失败 - {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


def test_service_instantiation():
    """测试服务实例化"""
    print("\n" + "=" * 60)
    print("🧪 重构验证 - 服务实例化测试")
    print("=" * 60)
    
    try:
        # 测试DirectQueryService（不需要LLM和数据库连接）
        from services.queries.direct_query import DirectQueryService
        from unittest.mock import Mock
        
        mock_db = Mock()
        service = DirectQueryService(mock_db)
        print("✅ DirectQueryService 实例化成功")
        
        # 测试安全检查功能
        is_safe, reason = service._is_safe_query("g.V().limit(5)")
        if is_safe:
            print("✅ 安全检查功能正常")
        else:
            print(f"⚠️ 安全检查异常: {reason}")
        
        return True
        
    except Exception as e:
        print(f"❌ 服务实例化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n开始重构验证...\n")
    
    # 测试1: 导入
    imports_ok = test_imports()
    
    # 测试2: 实例化
    services_ok = test_service_instantiation()
    
    # 总结
    print("\n" + "=" * 60)
    if imports_ok and services_ok:
        print("✅ 所有验证通过！重构成功！")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ 部分验证失败，请检查错误信息")
        print("=" * 60)
        sys.exit(1)
