# -*- coding: utf-8 -*-
"""
正确清理 HugeGraph 所有 Schema 元素的脚本
使用 PyHugeGraph 原生 API 获取所有定义的 Schema 元素，不管是否有数据
"""

import sys
import os
import time

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from pyhugegraph.client import PyHugeClient
from config import Config


def get_all_schema_elements_native(client):
    """使用原生API获取所有Schema元素"""
    schema = client.schema()
    
    # 获取所有顶点标签
    vertex_labels = []
    try:
        vertex_label_objects = schema.getVertexLabels()
        if isinstance(vertex_label_objects, list):
            vertex_labels = [vl.name for vl in vertex_label_objects]
    except Exception as e:
        print(f"⚠️  获取顶点标签失败: {e}")
    
    # 获取所有边标签  
    edge_labels = []
    try:
        edge_label_objects = schema.getEdgeLabels()
        if isinstance(edge_label_objects, list):
            edge_labels = [el.name for el in edge_label_objects]
    except Exception as e:
        print(f"⚠️  获取边标签失败: {e}")
    
    # 获取所有属性键
    property_keys = []
    try:
        property_key_objects = schema.getPropertyKeys()
        if isinstance(property_key_objects, list):
            property_keys = [pk.name for pk in property_key_objects]
    except Exception as e:
        print(f"⚠️  获取属性键失败: {e}")
    
    return vertex_labels, edge_labels, property_keys


def clear_all_schema_elements():
    """清理所有Schema元素"""
    print("🧹 开始清理所有 Schema 元素...")
    
    try:
        client = PyHugeClient(
            ip=Config.HUGEGRAPH_HOST,
            port=Config.HUGEGRAPH_PORT,
            user=Config.HUGEGRAPH_USER,
            pwd=Config.HUGEGRAPH_PWD,
            graph=Config.HUGEGRAPH_GRAPH
        )
        print(f"✅ 连接到 HugeGraph: {Config.HUGEGRAPH_HOST}:{Config.HUGEGRAPH_PORT}")
    except Exception as e:
        print(f"❌ 连接 HugeGraph 失败: {e}")
        return False
    
    # 首先清空所有数据
    print("🗑️  清空所有数据...")
    try:
        # 删除所有边
        result = client.gremlin().exec("g.E().drop()")
        print("   ✅ 所有边已删除")
        
        # 删除所有顶点  
        result = client.gremlin().exec("g.V().drop()")
        print("   ✅ 所有顶点已删除")
    except Exception as e:
        print(f"⚠️  数据清理异常: {e}")
    
    time.sleep(1)
    
    # 获取所有 Schema 元素（使用原生API）
    print("🔍 获取所有 Schema 元素...")
    vertex_labels, edge_labels, property_keys = get_all_schema_elements_native(client)
    
    print(f"📊 发现 Schema 元素:")
    print(f"   顶点标签: {len(vertex_labels)} 个 - {vertex_labels}")
    print(f"   边标签: {len(edge_labels)} 个 - {edge_labels}")
    print(f"   属性键: {len(property_keys)} 个 - {property_keys}")
    
    if not vertex_labels and not edge_labels and not property_keys:
        print("✅ 没有 Schema 元素需要清理")
        return True
    
    # 按正确顺序删除 Schema 元素
    schema = client.schema()
    
    # 1. 删除边标签
    if edge_labels:
        print("🗑️  删除边标签...")
        for edge_label in edge_labels:
            try:
                schema.edgeLabel(edge_label).remove()
                print(f"   ✅ 删除边标签: {edge_label}")
            except Exception as e:
                print(f"   ⚠️  删除边标签 {edge_label} 失败: {e}")
        time.sleep(1)
    
    # 2. 删除顶点标签
    if vertex_labels:
        print("🗑️  删除顶点标签...")
        for vertex_label in vertex_labels:
            try:
                schema.vertexLabel(vertex_label).remove()
                print(f"   ✅ 删除顶点标签: {vertex_label}")
            except Exception as e:
                print(f"   ⚠️  删除顶点标签 {vertex_label} 失败: {e}")
        time.sleep(1)
    
    # 3. 删除属性键
    if property_keys:
        print("🗑️  删除属性键...")
        for prop_key in property_keys:
            try:
                schema.propertyKey(prop_key).remove()
                print(f"   ✅ 删除属性键: {prop_key}")
            except Exception as e:
                print(f"   ⚠️  删除属性键 {prop_key} 失败: {e}")
        time.sleep(1)
    
    # 验证清理结果
    print("🔍 验证清理结果...")
    final_vl, final_el, final_pk = get_all_schema_elements_native(client)
    
    if not final_vl and not final_el and not final_pk:
        print("🎉 所有 Schema 元素已成功清理！")
        return True
    else:
        print("⚠️  清理未完全成功，请手动检查")
        print(f"   剩余顶点标签: {final_vl}")
        print(f"   剩余边标签: {final_el}")  
        print(f"   剩余属性键: {final_pk}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("HugeGraph 完整 Schema 清理工具")
    print("=" * 60)
    
    response = input("⚠️  此操作将删除所有数据和 Schema！确认继续吗？(yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ 操作已取消")
        return
    
    success = clear_all_schema_elements()
    
    if success:
        print("\n✅ 清理完成！图现在是完全空白的。")
    else:
        print("\n❌ 清理可能未完全成功，请检查错误信息。")
    
    print("=" * 60)


if __name__ == "__main__":
    main()