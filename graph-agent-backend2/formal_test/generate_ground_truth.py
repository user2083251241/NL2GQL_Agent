# -*- coding: utf-8 -*-
"""
正式测试用例 - Gremlin 答案生成脚本

功能：
1. 定义30个测试用例（简单、中等、复杂三个级别）
2. 使用标准 Gremlin 查询获取正确答案
3. 将结果保存为 JSON 格式，包含：
   - question: 自然语言问题
   - level: 难度级别 (simple/medium/complex)
   - gremlin_query: 对应的 Gremlin 查询
   - expected_answer: 预期答案（结构化数据）
   - description: 测试说明

使用方法：
python formal_test/generate_ground_truth.py
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.database.client import get_db


def execute_gremlin_query(db, query):
    """执行 Gremlin 查询并返回结果"""
    try:
        result = db.execute_gremlin(query)
        return {
            "success": True,
            "data": result.get("data", []),
            "count": len(result.get("data", []))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": [],
            "count": 0
        }


def generate_simple_queries():
    """生成简单查询测试用例（10条）"""
    queries = [
        {
            "id": 1,
            "question": "数据库中总共有多少部电影？",
            "level": "simple",
            "gremlin_query": "g.V().hasLabel('Movie').count()",
            "description": "统计 Movie 顶点总数"
        },
        {
            "id": 2,
            "question": "用户ID为1的用户给哪些电影评过分？",
            "level": "simple",
            "gremlin_query": "g.V().has('User', 'userId', 1).out('rated').values('movieId')",
            "description": "查询 User(1) 通过 rated 边连接的所有 Movie"
        },
        {
            "id": 3,
            "question": "动作类型的电影有哪些？",
            "level": "simple",
            "gremlin_query": "g.V().has('Genre', 'name', 'Action').in('belongsTo').values('title')",
            "description": "查找属于 Action 类型的所有电影标题"
        },
        {
            "id": 4,
            "question": "电影Toy Story (1995)的IMDb ID是什么？",
            "level": "simple",
            "gremlin_query": "g.V().has('Movie', 'title', 'Toy Story (1995)').values('imdbId')",
            "description": "查询指定电影的 IMDb ID"
        },
        {
            "id": 5,
            "question": "用户ID为5的用户标记过哪些电影？",
            "level": "simple",
            "gremlin_query": "g.V().has('User', 'userId', 5).out('tagged').values('movieId')",
            "description": "查询 User(5) 通过 tagged 边连接的所有 Movie"
        },
        {
            "id": 6,
            "question": "评分最高的电影是哪部？（评分=5.0）",
            "level": "simple",
            "gremlin_query": "g.E().hasLabel('rated').has('rating', 5.0).inV().values('title').dedup().limit(1)",
            "description": "查找评分为 5.0 的电影（去重后取第一个）"
        },
        {
            "id": 7,
            "question": "有多少个不同类型的电影？",
            "level": "simple",
            "gremlin_query": "g.V().hasLabel('Genre').count()",
            "description": "统计 Genre 顶点总数"
        },
        {
            "id": 8,
            "question": "用户ID为10的用户在什么时候给电影评过分？",
            "level": "simple",
            "gremlin_query": "g.V().has('User', 'userId', 10).outE('rated').values('timestamp')",
            "description": "查询 User(10) 的所有评分时间戳"
        },
        {
            "id": 9,
            "question": "电影ID为100的电影属于什么类型？",
            "level": "simple",
            "gremlin_query": "g.V().has('Movie', 'movieId', 100).out('belongsTo').values('name')",
            "description": "查询 Movie(100) 所属的所有类型名称"
        },
        {
            "id": 10,
            "question": "有多少用户给电影打过分？",
            "level": "simple",
            "gremlin_query": "g.V().hasLabel('User').where(out('rated').count().is(gt(0))).count()",
            "description": "统计至少给一部电影评过分的用户数量"
        }
    ]
    return queries


def generate_medium_queries():
    """生成中等查询测试用例（10条）"""
    queries = [
        {
            "id": 11,
            "question": "给Toy Story (1995)这部电影评分为5分的用户有哪些？",
            "level": "medium",
            "gremlin_query": "g.V().has('Movie', 'title', 'Toy Story (1995)').inE('rated').has('rating', 5.0).outV().values('userId')",
            "description": "查找对 Toy Story (1995) 评分为 5.0 的所有用户 ID"
        },
        {
            "id": 12,
            "question": "喜欢动作电影的用户平均给了多少分？",
            "level": "medium",
            "gremlin_query": "g.V().has('Genre', 'name', 'Action').in('belongsTo').inE('rated').values('rating').mean()",
            "description": "计算 Action 类型电影的平均评分"
        },
        {
            "id": 13,
            "question": "用户ID为1标记了哪些类型的电影？",
            "level": "medium",
            "gremlin_query": "g.V().has('User', 'userId', 1).out('tagged').out('belongsTo').values('name').dedup()",
            "description": "查询 User(1) 标记过的电影涉及的所有类型（去重）"
        },
        {
            "id": 14,
            "question": "哪些电影同时属于Comedy和Drama类型？",
            "level": "medium",
            "gremlin_query": "g.V().has('Genre', 'name', 'Comedy').in('belongsTo').aggregate('comedy').V().has('Genre', 'name', 'Drama').in('belongsTo').where(within('comedy')).values('title').dedup()",
            "description": "查找同时属于 Comedy 和 Drama 两种类型的电影"
        },
        {
            "id": 15,
            "question": "在2010年之后被标记的电影有哪些？",
            "level": "medium",
            "gremlin_query": "g.E().hasLabel('tagged').has('timestamp', gt(1262304000)).inV().values('movieId').dedup()",
            "description": "查找 2010-01-01 之后被标记的电影（时间戳 > 1262304000）"
        },
        {
            "id": 16,
            "question": "评分高于4分的科幻电影有哪些？",
            "level": "medium",
            "gremlin_query": "g.V().has('Genre', 'name', 'Sci-Fi').in('belongsTo').as('movie').inE('rated').has('rating', gt(4.0)).outV().select('movie').values('title').dedup()",
            "description": "查找 Sci-Fi 类型且评分 > 4.0 的电影标题"
        },
        {
            "id": 17,
            "question": "用户ID为5最喜欢的电影类型是什么？（基于评分最高的电影）",
            "level": "medium",
            "gremlin_query": "g.V().has('User', 'userId', 5).outE('rated').order().by('rating', decr).limit(1).inV().out('belongsTo').values('name')",
            "description": "找出 User(5) 评分最高的电影所属的类型"
        },
        {
            "id": 18,
            "question": "被最多用户评分的前5部电影是哪些？",
            "level": "medium",
            "gremlin_query": "g.V().hasLabel('Movie').project('title', 'rating_count').by(values('title')).by(inE('rated').count()).order().by('rating_count', decr).limit(5)",
            "description": "按评分次数排序，返回前 5 部电影及其评分次数"
        },
        {
            "id": 19,
            "question": "哪些用户既给电影评过分又标记过电影？",
            "level": "medium",
            "gremlin_query": "g.V().hasLabel('User').where(out('rated').count().is(gt(0))).where(out('tagged').count().is(gt(0))).values('userId')",
            "description": "查找既有 rated 边又有 tagged 边的用户"
        },
        {
            "id": 20,
            "question": "Adventure类型的电影平均评分是多少？",
            "level": "medium",
            "gremlin_query": "g.V().has('Genre', 'name', 'Adventure').in('belongsTo').inE('rated').values('rating').mean()",
            "description": "计算 Adventure 类型电影的平均评分"
        }
    ]
    return queries


def generate_complex_queries():
    """生成复杂查询测试用例（10条）"""
    queries = [
        {
            "id": 21,
            "question": "找出同时喜欢Action和Sci-Fi类型的用户的共同偏好电影？",
            "level": "complex",
            "gremlin_query": "g.V().has('Genre', 'name', 'Action').in('belongsTo').inE('rated').has('rating', gte(4.0)).outV().aggregate('action_users').V().has('Genre', 'name', 'Sci-Fi').in('belongsTo').inE('rated').has('rating', gte(4.0)).outV().where(within('action_users')).out('rated').inV().values('title').groupCount().order(local).by(values, decr).limit(10)",
            "description": "找出同时对 Action 和 Sci-Fi 电影评分 >= 4.0 的用户，返回他们共同喜欢的电影（按出现次数排序）"
        },
        {
            "id": 22,
            "question": "哪些电影被高评分用户（平均评分>4.5）评为5分，且属于热门类型？",
            "level": "complex",
            "gremlin_query": "g.V().hasLabel('User').as('user').outE('rated').values('rating').fold().math('_ / size(_)').is(gt(4.5)).select('user').outE('rated').has('rating', 5.0).inV().out('belongsTo').values('name').groupCount().order(local).by(values, decr).limit(3).select(keys).unfold().as('hot_genre').V().has('Genre', where(eq('hot_genre'))).in('belongsTo').inE('rated').has('rating', 5.0).outV().where(eq('user')).select('user').outE('rated').has('rating', 5.0).inV().values('title').dedup()",
            "description": "查找平均评分 > 4.5 的用户评为 5.0 分且属于最热门 3 种类型的电影"
        },
        {
            "id": 23,
            "question": "用户ID为1和用户ID为2的共同兴趣电影有哪些？（都评过分且评分>=4）",
            "level": "complex",
            "gremlin_query": "g.V().has('User', 'userId', 1).outE('rated').has('rating', gte(4.0)).inV().aggregate('user1_movies').V().has('User', 'userId', 2).outE('rated').has('rating', gte(4.0)).inV().where(within('user1_movies')).values('title')",
            "description": "找出 User(1) 和 User(2) 都评分 >= 4.0 的共同电影"
        },
        {
            "id": 24,
            "question": "找出在周末（周六、周日）被标记最多的电影类型？",
            "level": "complex",
            "gremlin_query": "g.E().hasLabel('tagged').has('timestamp', P.gt(0)).project('genre', 'timestamp').by(inV().out('belongsTo').values('name')).by(values('timestamp')).filter(select('timestamp').math('(_ % 86400) / 3600').is(gte(48))).select('genre').groupCount().order(local).by(values, decr).limit(5)",
            "description": "分析周末（简化处理）被标记最多的电影类型（注：实际需要根据时间戳转换为星期几）"
        },
        {
            "id": 25,
            "question": "哪些电影的评分标准差最小（评分最一致），且至少有10个用户评分？",
            "level": "complex",
            "gremlin_query": "g.V().hasLabel('Movie').as('movie').inE('rated').values('rating').fold().where(count(local).is(gte(10))).project('title', 'std_dev').by(select('movie').values('title')).by(math('sqrt((sum(x * x) - (sum(x) * sum(x) / count(x))) / count(x))')).order().by('std_dev', asc).limit(5)",
            "description": "找出评分至少 10 次且评分标准差最小的前 5 部电影"
        },
        {
            "id": 26,
            "question": "找出既被标记为经典又被高评分（>=4.5）的喜剧电影？",
            "level": "complex",
            "gremlin_query": "g.V().has('Genre', 'name', 'Comedy').in('belongsTo').as('movie').inE('rated').has('rating', gte(4.5)).outV().outE('tagged').has('tag', 'classic').inV().where(eq('movie')).select('movie').values('title')",
            "description": "查找 Comedy 类型、评分 >= 4.5 且被标记为 'classic' 的电影"
        },
        {
            "id": 27,
            "question": "用户的评分行为分析：哪些用户倾向于给特定类型电影更高评分？",
            "level": "complex",
            "gremlin_query": "g.V().hasLabel('User').as('user').outE('rated').as('rating_edge').inV().out('belongsTo').values('name').as('genre').select('rating_edge').values('rating').as('rating_val').select('user', 'genre', 'rating_val').group().by(select('user', 'genre')).by(select('rating_val').mean()).unfold().order().by(values, decr).limit(10)",
            "description": "分析每个用户对每种类型电影的平均评分，返回评分最高的 10 个组合"
        },
        {
            "id": 28,
            "question": "时间序列分析：哪些电影类型在不同时间段的受欢迎程度变化最大？",
            "level": "complex",
            "gremlin_query": "g.E().hasLabel('rated').project('genre', 'month', 'count').by(inV().out('belongsTo').values('name')).by(values('timestamp').math('(_ / 2592000) % 12').intValue()).by(constant(1)).group().by(select('genre', 'month')).by(select('count').sum()).unfold().group().by(select('genre')).by(select('count').fold()).unfold().project('genre', 'variance').by(select(keys).select('genre')).by(select(values).unfold().math('(x - mean)^2').fold().math('sum(_) / size(_)')).order().by('variance', decr).limit(5)",
            "description": "计算每种类型在不同月份的评分数量方差，找出变化最大的 5 种类型"
        },
        {
            "id": 29,
            "question": "找出评分分布最均匀的电影（各个评分等级都有，且数量相近）？",
            "level": "complex",
            "gremlin_query": "g.V().hasLabel('Movie').as('movie').inE('rated').values('rating').groupCount().as('dist').select('movie', 'dist').filter(select('dist').unfold().count(local).is(gte(3))).project('title', 'uniformity').by(select('movie').values('title')).by(select('dist').unfold().values().fold().math('max(_) - min(_)')).order().by('uniformity', asc).limit(5)",
            "description": "找出至少有 3 种不同评分且评分分布最均匀（最大值与最小值差异最小）的前 5 部电影"
        },
        {
            "id": 30,
            "question": "复合推荐：找出与用户ID为1品味相似的其他用户推荐但用户ID为1还未看过的电影？",
            "level": "complex",
            "gremlin_query": "g.V().has('User', 'userId', 1).out('rated').aggregate('seen_movies').inE('rated').has('rating', gte(4.0)).outV().where(neq('self')).as('similar_user').outE('rated').has('rating', gte(4.0)).inV().where(not(within('seen_movies'))).values('title').groupCount().order(local).by(values, decr).limit(10)",
            "description": "找出与 User(1) 有相似高分评价的其他用户推荐的、User(1) 未观看的高分电影"
        }
    ]
    return queries


def execute_all_tests():
    """执行所有测试用例并保存结果"""
    print("="*80)
    print("🚀 开始生成正式测试用例的正确答案")
    print("="*80)
    
    # 初始化数据库连接
    try:
        print("\n📦 正在连接图数据库...")
        db = get_db()
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return
    
    # 收集所有测试用例
    all_queries = []
    all_queries.extend(generate_simple_queries())
    all_queries.extend(generate_medium_queries())
    all_queries.extend(generate_complex_queries())
    
    print(f"\n📋 共 {len(all_queries)} 个测试用例")
    print(f"   - 简单查询: 10 个")
    print(f"   - 中等查询: 10 个")
    print(f"   - 复杂查询: 10 个")
    print("-"*80)
    
    # 执行每个测试用例
    results = []
    success_count = 0
    fail_count = 0
    
    for i, test_case in enumerate(all_queries, 1):
        print(f"\n[{i}/{len(all_queries)}] 执行测试 #{test_case['id']} ({test_case['level']})")
        print(f"   问题: {test_case['question']}")
        print(f"   Gremlin: {test_case['gremlin_query'][:60]}...")
        
        # 执行查询
        result = execute_gremlin_query(db, test_case['gremlin_query'])
        
        if result['success']:
            success_count += 1
            print(f"   ✅ 成功 - 返回 {result['count']} 条结果")
            
            # 保存结果
            test_result = {
                **test_case,
                "execution_result": {
                    "success": True,
                    "data": result['data'],
                    "count": result['count']
                },
                "generated_at": datetime.now().isoformat()
            }
            results.append(test_result)
        else:
            fail_count += 1
            print(f"   ❌ 失败 - 错误: {result['error']}")
            
            test_result = {
                **test_case,
                "execution_result": {
                    "success": False,
                    "error": result['error'],
                    "data": [],
                    "count": 0
                },
                "generated_at": datetime.now().isoformat()
            }
            results.append(test_result)
    
    # 保存结果到文件
    output_file = os.path.join(os.path.dirname(__file__), "ground_truth_answers.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print("\n" + "="*80)
    print("📊 测试执行总结")
    print("="*80)
    print(f"总测试数: {len(all_queries)}")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print(f"成功率: {(success_count / len(all_queries)) * 100:.1f}%")
    print(f"\n💾 结果已保存至: {output_file}")
    print("="*80)


if __name__ == "__main__":
    execute_all_tests()
