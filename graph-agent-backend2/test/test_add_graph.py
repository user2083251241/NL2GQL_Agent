"""
测试数据生成脚本 - 包含 Schema 清理、创建及数据插入功能

功能：
1. 删除现有的 Schema（顶点标签、边标签、属性键）
2. 创建符合测试数据的 Schema
3. 生成并插入 100 个节点和若干条边
"""
import sys
import os
import random

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.database.client import get_db

def drop_existing_schema(db):
    """删除数据库中已存在的 Schema"""
    print("\n🗑️ 步骤1: 清理现有 Schema...")
    
    # 1. 清空图数据
    print("  🧹 清空图数据...")
    db.execute_gremlin("g.E().drop()")
    db.execute_gremlin("g.V().drop()")
    
    # 2. 使用 pyhugegraph 原生 API 删除 Schema
    schema_manager = db._client.schema()
    
    # 删除边标签
    for label in schema_manager.getEdgeLabels():
        try:
            # label 是对象，通过 .name 获取名称
            schema_manager.edgeLabel(label.name).remove()
            print(f"  ✅ 已删除边标签: {label.name}")
        except Exception as e:
            print(f"  ⚠️ 删除边标签失败: {e}")
            
    # 删除顶点标签
    for label in schema_manager.getVertexLabels():
        try:
            schema_manager.vertexLabel(label.name).remove()
            print(f"  ✅ 已删除顶点标签: {label.name}")
        except Exception as e:
            print(f"  ⚠️ 删除顶点标签失败: {e}")
            
    # 删除属性键
    for prop in schema_manager.getPropertyKeys():
        try:
            schema_manager.propertyKey(prop.name).remove()
            print(f"  ✅ 已删除属性键: {prop.name}")
        except Exception as e:
            print(f"  ⚠️ 删除属性键失败: {e}")
            
    print("✅ Schema 清理完成！\n")

def create_test_schema(db):
    """创建测试所需的 Schema"""
    print("📋 步骤2: 创建新 Schema...")
    schema_manager = db._client.schema()
    
    # 1. 创建属性键
    properties = [
        ("name", "asText"),
        ("age", "asInt"),
        ("industry", "asText"),
        ("population", "asInt"),
        ("level", "asText"),
        ("status", "asText")
    ]
    
    for prop_name, method_name in properties:
        try:
            # 使用链式调用: schema.propertyKey('name').asText().ifNotExist().create()
            getattr(schema_manager.propertyKey(prop_name), method_name)().ifNotExist().create()
            print(f"  ✅ 创建属性键: {prop_name}")
        except Exception as e:
            print(f"  ⚠️ 属性键 {prop_name} 可能已存在: {e}")
            
    # 2. 创建顶点标签
    vertex_labels = {
        "Person": ["name", "age"],
        "Company": ["name", "industry"],
        "City": ["name", "population"],
        "Skill": ["name", "level"],
        "Project": ["name", "status"]
    }
    
    for label, props in vertex_labels.items():
        try:
            # 设置主键为 name
            schema_manager.vertexLabel(label).properties(*props).primaryKeys("name").ifNotExist().create()
            print(f"  ✅ 创建顶点标签: {label}")
        except Exception as e:
            print(f"  ⚠️ 顶点标签 {label} 创建失败: {e}")
            
    # 3. 创建边标签 (必须指定 sourceLabel 和 targetLabel)
    edge_definitions = [
        ("works_at", "Person", "Company"),
        ("lives_in", "Person", "City"),
        ("has_skill", "Person", "Skill"),
        ("participates_in", "Person", "Project"),
        ("located_in", "Company", "City")
    ]
    
    for label, src, dst in edge_definitions:
        try:
            schema_manager.edgeLabel(label).sourceLabel(src).targetLabel(dst).ifNotExist().create()
            print(f"  ✅ 创建边标签: {label} ({src} -> {dst})")
        except Exception as e:
            print(f"  ⚠️ 边标签 {label} 创建失败: {e}")
            
    print("✅ Schema 创建完成！\n")

def create_indexes(db):
    """创建必要的二级索引"""
    print("📈 步骤3: 创建二级索引...")
    schema_manager = db._client.schema()
    
    # 为 Company.industry 创建二级索引
    try:
        schema_manager.propertyKey('industry').asText().ifNotExist().create()
        schema_manager.indexLabel('CompanyByIndustry').onV('Company').by('industry').secondary().ifNotExist().create()
        print("  ✅ 创建 Company.industry 二级索引")
    except Exception as e:
        print(f"  ⚠️ 创建 Company.industry 索引失败: {e}")
        
    # 为 City.name 创建二级索引（虽然 name 是主键，但显式创建索引有助于查询优化）
    try:
        schema_manager.indexLabel('CityByName').onV('City').by('name').secondary().ifNotExist().create()
        print("  ✅ 创建 City.name 二级索引")
    except Exception as e:
        print(f"  ⚠️ 创建 City.name 索引失败: {e}")
        
    print("✅ 索引创建完成！\n")

def generate_and_insert_data(db):
    """生成并插入测试数据"""
    print("🚀 步骤3: 生成并插入数据...")
    
    # 1. 准备数据内容
    data = {
        "Person": [{"name": f"Person_{i}", "age": random.randint(20, 60)} for i in range(20)],
        "Company": [{"name": f"Company_{i}", "industry": random.choice(["Tech", "Finance"])} for i in range(20)],
        "City": [{"name": f"City_{i}", "population": random.randint(100000, 10000000)} for i in range(20)],
        "Skill": [{"name": f"Skill_{i}", "level": random.choice(["Junior", "Senior"])} for i in range(20)],
        "Project": [{"name": f"Project_{i}", "status": "Active"} for i in range(20)]
    }
    
    # 2. 插入顶点 (使用原生 API 更加稳定)
    graph_api = db._client.graph()
    for label, items in data.items():
        for item in items:
            try:
                # addVertex 接受 label 和 properties 字典
                graph_api.addVertex(label, item)
            except Exception as e:
                print(f"  ⚠️ 插入顶点 {item['name']} 失败: {e}")
    print("  ✅ 100 个顶点插入完成")
    
    # 3. 插入边 (修正 Gremlin 语法：通过属性查找顶点以确保 ID 正确)
    edges_added = 0
    relations = [
        ("Person", "works_at", "Company"),
        ("Person", "lives_in", "City"),
        ("Person", "has_skill", "Skill"),
        ("Person", "participates_in", "Project"),
        ("Company", "located_in", "City")
    ]
    
    for src_label, edge_label, dst_label in relations:
        src_names = [f"{src_label}_{i}" for i in range(20)]
        dst_names = [f"{dst_label}_{i}" for i in range(20)]
        
        for src_name in src_names:
            # 每个节点随机连 1-2 条边
            for _ in range(random.randint(1, 2)):
                dst_name = random.choice(dst_names)
                # 关键修正：使用 hasLabel 和 has('name', ...) 来精确定位顶点
                query = f"g.V().hasLabel('{src_label}').has('name', '{src_name}').addE('{edge_label}').to(__.V().hasLabel('{dst_label}').has('name', '{dst_name}'))"
                result = db.execute_gremlin(query)
                if result["success"] and result["data"]:
                    edges_added += 1
                
    print(f"  ✅ {edges_added} 条边插入完成\n")

if __name__ == "__main__":
    try:
        db = get_db()
        drop_existing_schema(db)
        create_test_schema(db)
        create_indexes(db)
        generate_and_insert_data(db)
        print("🎉 所有操作执行完毕！")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
