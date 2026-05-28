# -*- coding: utf-8 -*-
"""
测试用例答案查看工具

功能：
1. 查看所有测试用例列表
2. 查看特定测试用例的详细信息
3. 按难度级别筛选测试用例
4. 导出特定格式的测试结果

使用方法：
python formal_test/view_answers.py [选项]

示例：
python formal_test/view_answers.py --list                    # 列出所有测试用例
python formal_test/view_answers.py --id 1                    # 查看测试用例1
python formal_test/view_answers.py --level simple            # 查看所有简单查询
python formal_test/view_answers.py --stats                   # 查看统计信息
"""

import json
import sys
import os
import argparse
from typing import Dict, List, Any


def load_answers() -> List[Dict[str, Any]]:
    """加载基准答案文件"""
    answers_file = os.path.join(os.path.dirname(__file__), "ground_truth_answers.json")
    
    if not os.path.exists(answers_file):
        print(f"❌ 错误: 找不到答案文件 {answers_file}")
        print("请先运行 generate_ground_truth.py 生成答案")
        sys.exit(1)
    
    with open(answers_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_all_tests(answers: List[Dict[str, Any]]):
    """列出所有测试用例"""
    print("\n" + "="*80)
    print("📋 所有测试用例列表")
    print("="*80)
    
    # 按级别分组
    by_level = {"simple": [], "medium": [], "complex": []}
    for test in answers:
        by_level[test["level"]].append(test)
    
    # 显示简单查询
    print("\n🟢 简单查询 (Simple Queries)")
    print("-"*80)
    for test in by_level["simple"]:
        result_count = test["execution_result"]["count"]
        status = "✅" if test["execution_result"]["success"] else "❌"
        print(f"  [{test['id']:2d}] {status} {test['question'][:60]}")
        print(f"       结果数: {result_count}")
    
    # 显示中等查询
    print("\n🟡 中等查询 (Medium Queries)")
    print("-"*80)
    for test in by_level["medium"]:
        result_count = test["execution_result"]["count"]
        status = "✅" if test["execution_result"]["success"] else "❌"
        print(f"  [{test['id']:2d}] {status} {test['question'][:60]}")
        print(f"       结果数: {result_count}")
    
    # 显示复杂查询
    print("\n🔴 复杂查询 (Complex Queries)")
    print("-"*80)
    for test in by_level["complex"]:
        result_count = test["execution_result"]["count"]
        status = "✅" if test["execution_result"]["success"] else "❌"
        print(f"  [{test['id']:2d}] {status} {test['question'][:60]}")
        print(f"       结果数: {result_count}")
    
    print("\n" + "="*80)
    print(f"总计: {len(answers)} 个测试用例")
    print("="*80 + "\n")


def show_test_detail(answers: List[Dict[str, Any]], test_id: int):
    """显示特定测试用例的详细信息"""
    test = next((t for t in answers if t["id"] == test_id), None)
    
    if not test:
        print(f"❌ 错误: 找不到测试用例 #{test_id}")
        return
    
    print("\n" + "="*80)
    print(f"📝 测试用例 #{test['id']} 详细信息")
    print("="*80)
    
    print(f"\n问题:")
    print(f"  {test['question']}")
    
    print(f"\n难度级别:")
    level_names = {"simple": "简单", "medium": "中等", "complex": "复杂"}
    print(f"  {level_names.get(test['level'], test['level'])}")
    
    print(f"\n描述:")
    print(f"  {test['description']}")
    
    print(f"\nGremlin 查询:")
    query_lines = test['gremlin_query'].split('.')
    for i, line in enumerate(query_lines):
        if i == 0:
            print(f"  {line}.")
        elif i == len(query_lines) - 1:
            print(f"   {line}")
        else:
            print(f"   .{line}")
    
    print(f"\n执行结果:")
    exec_result = test["execution_result"]
    status = "✅ 成功" if exec_result["success"] else "❌ 失败"
    print(f"  状态: {status}")
    print(f"  结果数量: {exec_result['count']}")
    
    if exec_result["success"]:
        data = exec_result["data"]
        if isinstance(data, list):
            if len(data) <= 10:
                print(f"  结果数据: {data}")
            else:
                print(f"  结果数据 (前10条): {data[:10]}")
                print(f"  ... 共 {len(data)} 条")
        else:
            print(f"  结果数据: {data}")
    else:
        print(f"  错误信息: {exec_result.get('error', '未知错误')}")
    
    print(f"\n生成时间:")
    print(f"  {test['generated_at']}")
    
    print("\n" + "="*80 + "\n")


def filter_by_level(answers: List[Dict[str, Any]], level: str):
    """按难度级别筛选测试用例"""
    filtered = [t for t in answers if t["level"] == level]
    
    if not filtered:
        print(f"❌ 没有找到 '{level}' 级别的测试用例")
        return
    
    level_names = {"simple": "简单", "medium": "中等", "complex": "复杂"}
    print(f"\n{'='*80}")
    print(f"📊 {level_names.get(level, level)}查询测试用例 (共 {len(filtered)} 个)")
    print(f"{'='*80}\n")
    
    for test in filtered:
        result_count = test["execution_result"]["count"]
        status = "✅" if test["execution_result"]["success"] else "❌"
        print(f"[{test['id']:2d}] {status} {test['question']}")
        print(f"     Gremlin: {test['gremlin_query'][:70]}...")
        print(f"     结果数: {result_count}\n")


def show_statistics(answers: List[Dict[str, Any]]):
    """显示统计信息"""
    print("\n" + "="*80)
    print("📈 测试用例统计信息")
    print("="*80)
    
    # 总体统计
    total = len(answers)
    success = sum(1 for t in answers if t["execution_result"]["success"])
    failed = total - success
    
    print(f"\n总体情况:")
    print(f"  总测试数: {total}")
    print(f"  成功: {success} ({success/total*100:.1f}%)")
    print(f"  失败: {failed} ({failed/total*100:.1f}%)")
    
    # 按级别统计
    print(f"\n按难度级别:")
    by_level = {"simple": [], "medium": [], "complex": []}
    for test in answers:
        by_level[test["level"]].append(test)
    
    level_names = {"simple": "简单", "medium": "中等", "complex": "复杂"}
    for level, tests in by_level.items():
        count = len(tests)
        success_count = sum(1 for t in tests if t["execution_result"]["success"])
        avg_results = sum(t["execution_result"]["count"] for t in tests) / count if count > 0 else 0
        
        print(f"  {level_names[level]}:")
        print(f"    数量: {count}")
        print(f"    成功率: {success_count/count*100:.1f}%")
        print(f"    平均结果数: {avg_results:.1f}")
    
    # 结果分布
    print(f"\n结果数量分布:")
    result_counts = [t["execution_result"]["count"] for t in answers]
    if result_counts:
        print(f"  最小值: {min(result_counts)}")
        print(f"  最大值: {max(result_counts)}")
        print(f"  平均值: {sum(result_counts)/len(result_counts):.1f}")
        
        # 空结果统计
        empty_count = sum(1 for c in result_counts if c == 0)
        if empty_count > 0:
            print(f"  空结果: {empty_count} 个 ({empty_count/total*100:.1f}%)")
    
    print("\n" + "="*80 + "\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="测试用例答案查看工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python view_answers.py --list                    # 列出所有测试用例
  python view_answers.py --id 1                    # 查看测试用例1
  python view_answers.py --level simple            # 查看简单查询
  python view_answers.py --stats                   # 查看统计信息
        """
    )
    
    parser.add_argument("--list", action="store_true", help="列出所有测试用例")
    parser.add_argument("--id", type=int, help="查看特定测试用例的详细信息")
    parser.add_argument("--level", choices=["simple", "medium", "complex"], 
                       help="按难度级别筛选")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    
    args = parser.parse_args()
    
    # 如果没有提供任何参数，默认显示列表
    if not any([args.list, args.id, args.level, args.stats]):
        args.list = True
    
    # 加载答案
    answers = load_answers()
    
    # 执行相应操作
    if args.list:
        list_all_tests(answers)
    
    if args.id:
        show_test_detail(answers, args.id)
    
    if args.level:
        filter_by_level(answers, args.level)
    
    if args.stats:
        show_statistics(answers)


if __name__ == "__main__":
    main()
