# -*- coding: utf-8 -*-
"""
清空 HugeGraph 图数据和 Schema 脚本
删除所有顶点、边以及所有的 Schema 元素（边标签、顶点标签、属性键）
得到一个完全空白的图
"""

import sys
import os
import time

# 添加项目根目录到Python路径，以便正确导入modules
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.database.client import HugeGraphDB
from pyhugegraph.client import PyHugeClient
from config import Config


def get_all_schema_elements(db):
    """获取所有Schema元素的详细信息"""
    schema = db.get_schema()
    vertex_labels = schema.get('vertex_labels', [])
    edge_labels = schema.get('edge_labels', [])
    
    # 获取属性键列表
    property_keys = set()
    for props in schema.get('properties', {}).values():
        property_keys.update(props)
    property_keys = list(property_keys)
    
    return vertex_labels, edge_labels, property_keys


def clear_hugegraph_schema_and_data():
    """
    清空 HugeGraph 图中的所有数据和 Schema
    注意：Schema 删除必须按照正确的顺序进行
    """
    print("🧹 开始清空 HugeGraph 图数据和 Schema...")
    
    # 获取现有的数据库实例用于所有操作
    db = HugeGraphDB()
    
    # 1. 首先删除所有边
    print("🗑️  删除所有边...")
    try:
        result = db.execute_gremlin("g.E().drop()")
        if result['success']:
            print("✅ 所有边已删除")
        else:
            print(f"⚠️  边删除失败: {result['error']}")
    except Exception as e:
        print(f"⚠️  边删除异常: {e}")
    
    # 短暂等待
    time.sleep(1)
    
    # 2. 删除所有顶点
    print("🗑️  删除所有顶点...")
    try:
        result = db.execute_gremlin("g.V().drop()")
        if result['success']:
            print("✅ 所有顶点已删除")
        else:
            print(f"⚠️  顶点删除失败: {result['error']}")
    except Exception as e:
        print(f"⚠️  顶点删除异常: {e}")
    
    # 短暂等待
    time.sleep(1)
    
    # 3. 获取当前所有的 Schema 元素
    print("🔍 获取当前 Schema 信息...")
    vertex_labels, edge_labels, property_keys = get_all_schema_elements(db)
    
    print(f"📊 当前 Schema 状态:")
    print(f"   顶点标签: {len(vertex_labels)} 个")
    print(f"   边标签: {len(edge_labels)} 个") 
    print(f"   属性键: {len(property_keys)} 个")
    
    # 4. 如果没有 Schema 元素，直接返回
    if not vertex_labels and not edge_labels and not property_keys:
        print("✅ 图已经是空白状态！")
        return True
    
    # 5. 尝试使用原生 API 删除 Schema
    try:
        client = PyHugeClient(
            ip=Config.HUGEGRAPH_HOST,
            port=Config.HUGEGRAPH_PORT,
            user=Config.HUGEGRAPH_USER,
            pwd=Config.HUGEGRAPH_PWD,
            graph=Config.HUGEGRAPH_GRAPH
        )
        
        # 使用正确的 schema() 方法
        schema = client.schema()
        
        # 5.1 删除所有边标签
        if edge_labels:
            print("🗑️  删除边标签...")
            for edge_label in edge_labels:
                try:
                    schema.edgeLabel(edge_label).remove()
                    print(f"   ✅ 删除边标签: {edge_label}")
                except Exception as e:
                    print(f"   ⚠️  删除边标签 {edge_label} 失败: {e}")
            time.sleep(1)
        
        # 5.2 删除所有顶点标签
        if vertex_labels:
            print("🗑️  删除顶点标签...")
            for vertex_label in vertex_labels:
                try:
                    schema.vertexLabel(vertex_label).remove()
                    print(f"   ✅ 删除顶点标签: {vertex_label}")
                except Exception as e:
                    print(f"   ⚠️  删除顶点标签 {vertex_label} 失败: {e}")
            time.sleep(1)
        
        # 5.3 删除所有属性键
        if property_keys:
            print("🗑️  删除属性键...")
            for prop_key in property_keys:
                try:
                    schema.propertyKey(prop_key).remove()
                    print(f"   ✅ 删除属性键: {prop_key}")
                except Exception as e:
                    print(f"   ⚠️  删除属性键 {prop_key} 失败: {e}")
            time.sleep(1)
                    
    except Exception as e:
        print(f"⚠️  使用原生 API 删除 Schema 失败: {e}")
        print("🔄 尝试使用 Gremlin 方式清理...")
        # 如果原生 API 失败，尝试其他方式
        pass
    
    # 6. 验证清理结果
    print("🔍 验证清理结果...")
    final_vertex_labels, final_edge_labels, final_property_keys = get_all_schema_elements(db)
    final_vertex_count = db.execute_gremlin("g.V().count()")['data'][0] if db.execute_gremlin("g.V().count()")['success'] else -1
    final_edge_count = db.execute_gremlin("g.E().count()")['data'][0] if db.execute_gremlin("g.E().count()")['success'] else -1
    
    print(f"📊 最终状态:")
    print(f"   顶点数: {final_vertex_count}")
    print(f"   边数: {final_edge_count}")
    print(f"   顶点标签: {len(final_vertex_labels)} 个")
    print(f"   边标签: {len(final_edge_labels)} 个")
    
    if (final_vertex_count == 0 and final_edge_count == 0 and 
        len(final_vertex_labels) == 0 and len(final_edge_labels) == 0):
        print("🎉 HugeGraph 图已完全清空！")
        return True
    else:
        print("⚠️  清理可能未完全成功，请手动检查")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("HugeGraph 图清空工具")
    print("=" * 60)
    
    # 确认操作
    print(f"⚠️  此操作将永久删除图 '{Config.HUGEGRAPH_GRAPH}' 中的所有数据和 Schema！")
    print("⚠️  该操作无法撤销！")
    
    response = input("\n确认继续吗？(yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ 操作已取消")
        return
    
    success = clear_hugegraph_schema_and_data()
    
    if success:
        print("\n✅ 清空操作完成！图现在是完全空白的。")
    else:
        print("\n❌ 清空操作可能未完全成功，请检查日志。")
        print("💡 建议：如果仍有问题，可以尝试重启 HugeGraph Server 后重试")
    
    print("=" * 60)


if __name__ == "__main__":
    main()