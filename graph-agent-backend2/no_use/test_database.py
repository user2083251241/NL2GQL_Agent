"""
数据库模块测试脚本
用于验证HugeGraph连接和Schema提取功能
"""
from modules.database.client import HugeGraphDB


def test_database():
    """测试数据库功能"""
    print("=" * 60)
    print("🧪 数据库模块测试")
    print("=" * 60)
    
    # 1. 测试连接
    print("\n1️⃣ 测试数据库连接...")
    db = HugeGraphDB()
    
    if db.test_connection():
        print("✅ 数据库连接成功")
    else:
        print("❌ 数据库连接失败")
        return
    
    # 2. 测试Gremlin执行
    print("\n2️⃣ 测试Gremlin查询执行...")
    result = db.execute_gremlin("g.V().count()")
    print(f"   查询结果: {result}")
    
    if result["success"]:
        print(f"✅ 查询成功，顶点数量: {result['data']}")
    else:
        print(f"❌ 查询失败: {result.get('error')}")
    
    # 3. 测试Schema获取
    print("\n3️⃣ 测试Schema获取...")
    schema = db.get_schema()
    
    print(f"\n   顶点标签 ({len(schema['vertex_labels'])}个):")
    for label in schema['vertex_labels']:
        print(f"     - {label}")
    
    print(f"\n   边标签 ({len(schema['edge_labels'])}个):")
    for label in schema['edge_labels']:
        print(f"     - {label}")
    
    print(f"\n   属性信息:")
    for label, props in schema['properties'].items():
        print(f"     {label}: {props}")
    
    # 4. 测试格式化Schema文本
    print("\n4️⃣ 测试格式化Schema文本...")
    schema_text = db.get_schema_text()
    print("\n" + schema_text)
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_database()
