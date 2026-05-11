# -*- coding: utf-8 -*-
"""
专门清理 HugeGraph 属性键的脚本
用于解决属性键残留问题
"""

import sys
import os

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from pyhugegraph.client import PyHugeClient
from config import Config


def clear_all_property_keys():
    """清理所有属性键"""
    print("🧹 开始清理所有属性键...")
    
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
    
    # 获取所有属性键 - 使用正确的API
    try:
        # 使用 schema() 方法获取Schema管理器
        schema = client.schema()
        
        # 获取所有属性键 - 使用正确的方法名
        property_keys_response = schema.getPropertyKeys()
        
        # PyHugeGraph 返回的是属性键对象列表，需要提取名称
        if isinstance(property_keys_response, list):
            # 每个元素是一个属性键对象，通过 .name 获取名称
            property_keys = [prop.name for prop in property_keys_response]
        else:
            # 如果返回其他格式，尝试处理
            property_keys = []
            print(f"⚠️  无法解析属性键响应格式: {type(property_keys_response)}")
        
        print(f"🔍 发现 {len(property_keys)} 个属性键: {property_keys}")
        
        if not property_keys:
            print("✅ 没有属性键需要清理")
            return True
            
        # 删除所有属性键
        for prop_key in property_keys:
            try:
                # 使用正确的删除方法
                schema.propertyKey(prop_key).remove()
                print(f"   ✅ 删除属性键: {prop_key}")
            except Exception as e:
                print(f"   ⚠️  删除属性键 {prop_key} 失败: {e}")
                
        print("✅ 所有属性键清理完成！")
        return True
        
    except Exception as e:
        print(f"❌ 获取或删除属性键失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("HugeGraph 属性键清理工具")
    print("=" * 50)
    
    response = input("⚠️  此操作将删除所有属性键！确认继续吗？(yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ 操作已取消")
        return
    
    success = clear_all_property_keys()
    
    if success:
        print("\n🎉 属性键清理完成！")
    else:
        print("\n❌ 属性键清理失败，请检查错误信息。")
    
    print("=" * 50)


if __name__ == "__main__":
    main()