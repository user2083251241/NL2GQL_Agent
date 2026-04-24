"""
Agent模块测试脚本
用于验证GraphQueryAgent的核心功能
"""
import sys
from modules.llm.client import get_llm
from modules.database.client import get_db
from services.agents.agent import GraphQueryAgent


def test_agent_creation():
    """测试Agent创建"""
    print("=" * 60)
    print("🧪 Agent模块测试 - 创建Agent")
    print("=" * 60)
    sys.stdout.flush()
    
    try:
        # 获取LLM和数据库实例
        print("\n1️⃣ 初始化依赖...")
        llm = get_llm()
        db = get_db()
        print("✅ LLM和数据库初始化成功")
        sys.stdout.flush()
        
        # 创建Agent
        print("\n2️⃣ 创建GraphQueryAgent...")
        agent = GraphQueryAgent(llm=llm, db=db, max_retries=2)
        print("✅ Agent创建成功")
        sys.stdout.flush()
        
        return agent
        
    except Exception as e:
        print(f"❌ Agent创建失败: {e}")
        sys.stdout.flush()
        return None


def test_schema_info(agent):
    """测试获取Schema信息"""
    print("\n" + "=" * 60)
    print("📊 测试获取Schema信息")
    print("=" * 60)
    sys.stdout.flush()
    
    try:
        schema = agent.get_schema_info()
        
        print(f"\n顶点标签 ({len(schema.get('vertex_labels', []))}个):")
        for label in schema.get('vertex_labels', []):
            print(f"  - {label}")
        
        print(f"\n边标签 ({len(schema.get('edge_labels', []))}个):")
        for label in schema.get('edge_labels', []):
            print(f"  - {label}")
        
        print("\n✅ Schema信息获取成功")
        sys.stdout.flush()
        return True
        
    except Exception as e:
        print(f"❌ Schema获取失败: {e}")
        sys.stdout.flush()
        return False


def test_simple_query(agent):
    """测试简单查询"""
    print("\n" + "=" * 60)
    print("🔍 测试简单查询")
    print("=" * 60)
    sys.stdout.flush()
    
    question = "查询所有顶点的数量"
    print(f"\n用户问题: {question}")
    sys.stdout.flush()
    
    try:
        result = agent.process_query(question)
        
        print(f"\n{'='*60}")
        print("📋 查询结果:")
        print(f"{'='*60}")
        print(f"成功: {result['success']}")
        print(f"Gremlin: {result.get('gremlin', 'N/A')}")
        print(f"重试次数: {result.get('retries', 0)}")
        print(f"\n解释:")
        print(result.get('explanation', '无'))
        
        if result['success']:
            print("\n✅ 简单查询测试成功")
        else:
            print(f"\n⚠️ 查询失败: {result.get('error', '未知错误')}")
        
        sys.stdout.flush()
        return result['success']
        
    except Exception as e:
        print(f"❌ 查询异常: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🚀 开始Agent模块完整测试")
    print("=" * 60 + "\n")
    sys.stdout.flush()
    
    # 测试1: 创建Agent
    agent = test_agent_creation()
    
    if agent is None:
        print("\n⚠️ Agent创建失败，跳过后续测试")
        print("\n💡 提示: 请确保LLM和数据库配置正确")
        sys.stdout.flush()
        return
    
    # 测试2: 获取Schema
    test_schema_info(agent)
    
    # 测试3: 简单查询
    test_simple_query(agent)
    
    print("\n" + "=" * 60)
    print("✅ Agent模块测试完成")
    print("=" * 60)
    print("\n💡 提示: 如果查询较慢，是因为LLM API调用需要时间")
    print("=" * 60)
    sys.stdout.flush()


if __name__ == "__main__":
    main()
