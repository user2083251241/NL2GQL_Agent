# -*- coding: utf-8 -*-
"""
HugeGraph Gremlin 交互式查询工具

功能：
1. 提供命令行交互界面，直接输入 Gremlin 查询语句
2. 自动格式化显示查询结果
3. 支持查询历史记录
4. 内置常用命令（help、schema、exit等）
5. 错误处理和超时控制

使用方法：
python test/test_gremlin_query.py
"""

import sys
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.database.client import get_db


class GremlinQueryTool:
    """Gremlin 交互式查询工具"""
    
    def __init__(self):
        """初始化工具"""
        self.db = get_db()
        self.query_history: List[Dict[str, Any]] = []
        self.is_running = True
        
    def display_welcome(self):
        """显示欢迎信息"""
        print("\n" + "="*80)
        print("🔍 HugeGraph Gremlin 交互式查询工具")
        print("="*80)
        print("\n💡 使用提示：")
        print("  - 直接输入 Gremlin 查询语句（如：g.V().limit(5)）")
        print("  - 输入 'help' 查看帮助信息")
        print("  - 输入 'schema' 查看数据库 Schema")
        print("  - 输入 'history' 查看查询历史")
        print("  - 输入 'exit' 或 'quit' 退出程序")
        print("  - 多行查询以分号 (;) 结尾后按回车执行")
        print("="*80 + "\n")
    
    def display_help(self):
        """显示帮助信息"""
        print("\n" + "-"*80)
        print("📖 帮助信息")
        print("-"*80)
        print("\n【基本用法】")
        print("  直接输入 Gremlin 查询语句，例如：")
        print("    g.V().limit(5)")
        print("    g.V().has('Movie', 'title', 'Toy Story (1995)')")
        print("    g.V().hasLabel('User').count()")
        print("\n【内置命令】")
        print("  help       - 显示此帮助信息")
        print("  schema     - 查看数据库 Schema 信息")
        print("  history    - 查看最近的查询历史")
        print("  clear      - 清屏")
        print("  export N   - 导出第 N 条查询结果为 JSON 文件")
        print("  exit/quit  - 退出程序")
        print("\n【查询示例】")
        print("  1. 查询所有顶点（限制数量）：")
        print("     g.V().limit(10)")
        print("\n  2. 按标签查询：")
        print("     g.V().hasLabel('Movie').limit(5)")
        print("\n  3. 属性过滤：")
        print("     g.V().has('Movie', 'title', 'Toy Story (1995)')")
        print("\n  4. 统计查询：")
        print("     g.V().hasLabel('User').count()")
        print("\n  5. 边查询：")
        print("     g.E().hasLabel('rated').limit(5)")
        print("\n  6. 遍历查询：")
        print("     g.V().has('User', 'userId', 1).outE('rated').inV().values('title')")
        print("-"*80 + "\n")
    
    def display_schema(self):
        """显示数据库 Schema"""
        print("\n" + "-"*80)
        print("📊 数据库 Schema 信息")
        print("-"*80)
        
        try:
            schema = self.db.get_schema()
            
            if "error" in schema:
                print(f"❌ 获取 Schema 失败: {schema['error']}")
                return
            
            # 显示顶点标签
            vertex_labels = schema.get("vertex_labels", [])
            print(f"\n📌 顶点标签 ({len(vertex_labels)} 个):")
            for label in vertex_labels:
                props = schema.get("properties", {}).get(label, [])
                if props:
                    print(f"  • {label} - 属性: {', '.join(props)}")
                else:
                    print(f"  • {label}")
            
            # 显示边标签
            edge_labels = schema.get("edge_labels", [])
            print(f"\n🔗 边标签 ({len(edge_labels)} 个):")
            for label in edge_labels:
                print(f"  • {label}")
            
            print("\n" + "-"*80 + "\n")
            
        except Exception as e:
            print(f"❌ 获取 Schema 异常: {str(e)}\n")
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """
        执行 Gremlin 查询
        
        Args:
            query: Gremlin 查询语句
            
        Returns:
            查询结果字典
        """
        try:
            print(f"\n⏳ 执行查询: {query}")
            result = self.db.execute_gremlin(query)
            
            if result["success"]:
                data = result.get("data", [])
                count = result.get("count", len(data) if isinstance(data, list) else 1)
                
                return {
                    "success": True,
                    "data": data,
                    "count": count,
                    "timestamp": datetime.now().isoformat(),
                    "query": query
                }
            else:
                error_msg = result.get("error", "未知错误")
                return {
                    "success": False,
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat(),
                    "query": query
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"执行异常: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "query": query
            }
    
    def format_result(self, result: Dict[str, Any]):
        """格式化显示查询结果"""
        print("\n" + "="*80)
        
        if result["success"]:
            print("✅ 查询成功")
            print(f"📊 结果数量: {result['count']}")
            print(f"⏰ 执行时间: {result['timestamp']}")
            
            data = result.get("data", [])
            
            if isinstance(data, list):
                if len(data) == 0:
                    print("\n📭 返回空列表")
                elif len(data) <= 10:
                    # 结果较少时，完整显示
                    print(f"\n📋 查询结果:")
                    print(json.dumps(data, ensure_ascii=False, indent=2))
                else:
                    # 结果较多时，显示前10条和统计信息
                    print(f"\n📋 查询结果（显示前 10 条，共 {len(data)} 条）:")
                    print(json.dumps(data[:10], ensure_ascii=False, indent=2))
                    print(f"\n... 还有 {len(data) - 10} 条结果未显示")
            else:
                # 非列表类型结果（如计数、平均值等）
                print(f"\n📋 查询结果:")
                print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print("❌ 查询失败")
            print(f"⏰ 执行时间: {result['timestamp']}")
            print(f"🔴 错误信息: {result['error']}")
        
        print("="*80 + "\n")
    
    def save_to_history(self, query: str, result: Dict[str, Any]):
        """保存查询到历史记录"""
        self.query_history.append({
            "query": query,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        # 限制历史记录数量为最近50条
        if len(self.query_history) > 50:
            self.query_history = self.query_history[-50:]
    
    def display_history(self):
        """显示查询历史"""
        print("\n" + "-"*80)
        print("📜 查询历史（最近 {} 条）".format(len(self.query_history)))
        print("-"*80)
        
        if not self.query_history:
            print("\n📭 暂无查询历史\n")
            return
        
        for i, record in enumerate(reversed(self.query_history[-10:]), 1):
            status = "✅" if record["result"]["success"] else "❌"
            query_preview = record["query"][:60] + "..." if len(record["query"]) > 60 else record["query"]
            print(f"{i}. {status} {query_preview}")
            print(f"   时间: {record['timestamp']}")
        
        print("\n💡 提示: 输入 'export N' 可导出第 N 条历史记录为 JSON 文件")
        print("-"*80 + "\n")
    
    def export_history(self, index: int):
        """导出指定索引的历史记录为 JSON 文件"""
        if index < 1 or index > len(self.query_history):
            print(f"❌ 无效的索引值，当前历史记录范围: 1-{len(self.query_history)}\n")
            return
        
        # 注意：index是从1开始的，而列表是从0开始的，且历史记录是倒序显示的
        actual_index = len(self.query_history) - index
        record = self.query_history[actual_index]
        
        filename = f"gremlin_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
            print(f"✅ 查询结果已导出到: {filepath}\n")
        except Exception as e:
            print(f"❌ 导出失败: {str(e)}\n")
    
    def process_command(self, user_input: str) -> bool:
        """
        处理用户输入的命令
        
        Args:
            user_input: 用户输入的字符串
            
        Returns:
            是否继续运行
        """
        # 去除首尾空白
        command = user_input.strip()
        
        # 空输入
        if not command:
            return True
        
        # 退出命令
        if command.lower() in ['exit', 'quit', 'q']:
            print("\n👋 感谢使用，再见！\n")
            return False
        
        # 帮助命令
        if command.lower() == 'help':
            self.display_help()
            return True
        
        # Schema 命令
        if command.lower() == 'schema':
            self.display_schema()
            return True
        
        # 历史命令
        if command.lower() == 'history':
            self.display_history()
            return True
        
        # 清屏命令
        if command.lower() == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            self.display_welcome()
            return True
        
        # 导出命令
        if command.lower().startswith('export '):
            try:
                index = int(command.split()[1])
                self.export_history(index)
            except (ValueError, IndexError):
                print("❌ 用法: export <索引号>\n")
            return True
        
        # 否则作为 Gremlin 查询执行
        result = self.execute_query(command)
        self.format_result(result)
        self.save_to_history(command, result)
        
        return True
    
    def run(self):
        """运行交互式查询工具"""
        self.display_welcome()
        
        try:
            while self.is_running:
                try:
                    # 获取用户输入
                    user_input = input("gremlin> ")
                    
                    # 处理多行输入（以分号结尾）
                    if user_input.endswith(';'):
                        # 移除末尾的分号
                        user_input = user_input[:-1].strip()
                        
                        # 继续读取直到用户输入完成
                        lines = [user_input]
                        while True:
                            line = input("       ... ")
                            if line.strip().endswith(';'):
                                lines.append(line.strip()[:-1])
                                break
                            else:
                                lines.append(line)
                        
                        user_input = ' '.join(lines)
                    
                    # 处理命令
                    self.is_running = self.process_command(user_input)
                    
                except KeyboardInterrupt:
                    print("\n\n⚠️  检测到中断信号")
                    if input("确定要退出吗？(y/n): ").lower() == 'y':
                        print("\n👋 感谢使用，再见！\n")
                        break
                    else:
                        continue
                        
                except EOFError:
                    print("\n\n👋 感谢使用，再见！\n")
                    break
                    
        except Exception as e:
            print(f"\n❌ 程序异常: {str(e)}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    tool = GremlinQueryTool()
    tool.run()


if __name__ == "__main__":
    main()
