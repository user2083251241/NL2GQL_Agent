"""
测试数据生成脚本 - 向HugeGraph批量插入图数据

功能：
1. 生成大规模测试数据（可配置节点数量）
2. 自动创建Schema（顶点标签、边标签、属性）
3. 批量插入顶点和边
4. 支持多种场景：社交网络、知识图谱、企业关系

使用方式：
    python scripts/generate_test_data.py --vertices 1000 --edges 5000
"""
import sys
import os
import random
import argparse
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.database.client import HugeGraphDB
from config import Config


class TestDataGenerator:
    """测试数据生成器"""
    
    def __init__(self, db: HugeGraphDB):
        self.db = db
        self.vertex_count = 0
        self.edge_count = 0
        
        # 测试数据池
        self.first_names = [
            "张伟", "李娜", "王芳", "刘洋", "陈静", "杨磊", "赵敏", "黄强", 
            "周杰", "吴倩", "徐明", "孙丽", "马超", "朱琳", "胡军", "郭艳",
            "林峰", "何梅", "高峰", "罗婷", "梁勇", "宋佳", "郑浩", "谢芳",
            "韩磊", "唐丽", "冯杰", "于敏", "董伟", "袁静", "潘强", "蔡敏",
            "蒋华", "余倩", "杜明", "叶丽", "程军", "魏艳", "薛峰", "阎梅"
        ]
        
        self.last_names = [
            "建国", "志强", "秀英", "丽华", "伟", "芳", "敏", "静", 
            "磊", "洋", "勇", "艳", "杰", "涛", "明", "超", "秀兰", "霞",
            "平", "辉", "玲", "桂英", "凤", "兰", "刚", "利", "斌", "燕"
        ]
        
        self.cities = [
            "北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京",
            "西安", "重庆", "天津", "苏州", "长沙", "郑州", "济南", "青岛",
            "大连", "厦门", "宁波", "合肥"
        ]
        
        self.companies = [
            ("阿里巴巴", "互联网", "大型"),
            ("腾讯", "互联网", "大型"),
            ("百度", "互联网", "大型"),
            ("华为", "通信", "大型"),
            ("小米", "硬件", "中型"),
            ("字节跳动", "互联网", "大型"),
            ("美团", "互联网", "大型"),
            ("京东", "电商", "大型"),
            ("网易", "游戏", "中型"),
            ("滴滴", "出行", "中型"),
            ("拼多多", "电商", "中型"),
            ("快手", "短视频", "中型"),
            ("哔哩哔哩", "视频", "中型"),
            ("知乎", "社区", "小型"),
            ("小红书", "社区", "小型"),
            ("蔚来", "汽车", "中型"),
            ("小鹏", "汽车", "中型"),
            ("理想", "汽车", "小型"),
            ("商汤科技", "AI", "中型"),
            ("旷视科技", "AI", "中型")
        ]
        
        self.skills = [
            "Python", "Java", "JavaScript", "Go", "C++", "Rust", "TypeScript",
            "React", "Vue", "Angular", "Spring Boot", "Django", "Flask",
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
            "Docker", "Kubernetes", "AWS", "Azure", "GCP",
            "机器学习", "深度学习", "自然语言处理", "计算机视觉",
            "数据分析", "数据挖掘", "大数据", "云计算",
            "微服务", "分布式系统", "高并发", "性能优化"
        ]
        
        self.job_titles = [
            "软件工程师", "高级软件工程师", "技术专家", "架构师",
            "产品经理", "数据科学家", "算法工程师", "前端工程师",
            "后端工程师", "全栈工程师", "DevOps工程师", "测试工程师",
            "技术总监", "CTO", "CEO", "运营经理", "市场总监"
        ]
    
    def _escape_string(self, s: str) -> str:
        """转义字符串中的特殊字符"""
        return s.replace("'", "\\'").replace('"', '\\"')
    
    def create_schema(self):
        """创建图数据库Schema"""
        print("\n📋 步骤1: 创建Schema...")
        
        try:
            # 创建属性键
            properties = [
                ("name", "TEXT"),
                ("age", "INT"),
                ("city", "TEXT"),
                ("job_title", "TEXT"),
                ("industry", "TEXT"),
                ("scale", "TEXT"),
                ("proficiency", "TEXT"),
                ("since", "DATE"),
                ("amount", "DOUBLE")
            ]
            
            for prop_name, prop_type in properties:
                try:
                    query = f"schema.propertyKey('{prop_name}').as{prop_type}().ifNotExist().create()"
                    result = self.db.execute_gremlin(query)
                    if result["success"]:
                        print(f"  ✅ 创建属性键: {prop_name} ({prop_type})")
                    else:
                        print(f"  ⚠️ 属性键已存在或创建失败: {prop_name}")
                except Exception as e:
                    print(f"  ⚠️ 跳过属性键 {prop_name}: {e}")
            
            # 创建顶点标签
            vertex_labels = [
                ("Person", ["name", "age", "city", "job_title"]),
                ("Company", ["name", "industry", "scale"]),
                ("Skill", ["name"])
            ]
            
            for label, properties_list in vertex_labels:
                try:
                    props_str = ", ".join([f"'{p}'" for p in properties_list])
                    query = f"schema.vertexLabel('{label}').properties({props_str}).primaryKeys('name').ifNotExist().create()"
                    result = self.db.execute_gremlin(query)
                    if result["success"]:
                        print(f"  ✅ 创建顶点标签: {label}")
                    else:
                        print(f"  ⚠️ 顶点标签已存在或创建失败: {label}")
                except Exception as e:
                    print(f"  ⚠️ 跳过顶点标签 {label}: {e}")
            
            # 创建边标签
            edge_labels = [
                ("knows", ["since"]),
                ("works_at", []),
                ("has_skill", ["proficiency"]),
                ("invests_in", ["amount"])
            ]
            
            for label, properties_list in edge_labels:
                try:
                    props_str = ", ".join([f"'{p}'" for p in properties_list]) if properties_list else ""
                    if props_str:
                        query = f"schema.edgeLabel('{label}').properties({props_str}).ifNotExist().create()"
                    else:
                        query = f"schema.edgeLabel('{label}').ifNotExist().create()"
                    result = self.db.execute_gremlin(query)
                    if result["success"]:
                        print(f"  ✅ 创建边标签: {label}")
                    else:
                        print(f"  ⚠️ 边标签已存在或创建失败: {label}")
                except Exception as e:
                    print(f"  ⚠️ 跳过边标签 {label}: {e}")
            
            print("✅ Schema创建完成！\n")
            
        except Exception as e:
            print(f"❌ Schema创建失败: {e}\n")
    
    def generate_persons(self, count: int) -> list:
        """生成人物节点数据"""
        persons = []
        for i in range(count):
            name = random.choice(self.first_names) + random.choice(self.last_names)
            age = random.randint(22, 60)
            city = random.choice(self.cities)
            job_title = random.choice(self.job_titles)
            
            persons.append({
                "name": name,
                "age": age,
                "city": city,
                "job_title": job_title
            })
        
        return persons
    
    def generate_companies(self) -> list:
        """生成公司节点数据"""
        companies = []
        for name, industry, scale in self.companies:
            companies.append({
                "name": name,
                "industry": industry,
                "scale": scale
            })
        
        return companies
    
    def generate_skills(self) -> list:
        """生成技能节点数据"""
        skills = []
        for skill_name in self.skills:
            skills.append({
                "name": skill_name
            })
        
        return skills
    
    def insert_vertices_batch(self, vertices: list, label: str, batch_size: int = 100):
        """批量插入顶点"""
        print(f"  📝 插入 {label} 顶点 (共{len(vertices)}个)...")
        
        total_inserted = 0
        for i in range(0, len(vertices), batch_size):
            batch = vertices[i:i + batch_size]
            
            # 构建批量插入的Gremlin语句
            gremlin_parts = []
            for vertex in batch:
                props = []
                for key, value in vertex.items():
                    if isinstance(value, str):
                        props.append(f"'{key}', '{self._escape_string(value)}'")
                    elif isinstance(value, int):
                        props.append(f"'{key}', {value}")
                    elif isinstance(value, float):
                        props.append(f"'{key}', {value}")
                
                props_str = ", ".join(props)
                gremlin_parts.append(f"addV('{label}').property('{self._escape_string(vertex['name'])}').property({props_str})")
            
            # 合并为一个事务执行
            full_query = "g.inject(1)." + ".".join(gremlin_parts)
            
            result = self.db.execute_gremlin(full_query)
            if result["success"]:
                total_inserted += len(batch)
            else:
                print(f"  ❌ 批次插入失败: {result.get('error', '未知错误')}")
        
        self.vertex_count += total_inserted
        print(f"  ✅ 成功插入 {total_inserted} 个 {label} 顶点\n")
    
    def generate_and_insert_edges(self, persons: list, companies: list, skills: list, 
                                  target_edge_count: int):
        """生成并插入边关系"""
        print(f"  📝 生成并插入边关系 (目标{target_edge_count}条)...")
        
        edges_generated = 0
        batch_edges = []
        batch_size = 50
        
        # 1. works_at 关系 (每个人工作在某个公司)
        for person in persons:
            company = random.choice(companies)
            since_date = (datetime.now() - timedelta(days=random.randint(30, 3650))).strftime('%Y-%m-%d')
            
            edge = {
                "type": "works_at",
                "from_label": "Person",
                "from_name": person["name"],
                "to_label": "Company",
                "to_name": company["name"],
                "properties": [("since", f"'{since_date}'")]
            }
            batch_edges.append(edge)
            edges_generated += 1
            
            if len(batch_edges) >= batch_size:
                self._insert_edges_batch(batch_edges)
                batch_edges = []
        
        # 2. has_skill 关系 (每个人掌握多个技能)
        for person in persons:
            num_skills = random.randint(2, 8)
            person_skills = random.sample(skills, min(num_skills, len(skills)))
            
            for skill in person_skills:
                proficiency = random.choice(["初级", "中级", "高级", "专家"])
                
                edge = {
                    "type": "has_skill",
                    "from_label": "Person",
                    "from_name": person["name"],
                    "to_label": "Skill",
                    "to_name": skill["name"],
                    "properties": [("proficiency", f"'{proficiency}'")]
                }
                batch_edges.append(edge)
                edges_generated += 1
                
                if len(batch_edges) >= batch_size:
                    self._insert_edges_batch(batch_edges)
                    batch_edges = []
                
                if edges_generated >= target_edge_count * 0.7:  # 70%用于技能关系
                    break
            
            if edges_generated >= target_edge_count * 0.7:
                break
        
        # 3. knows 关系 (人与人之间的认识关系)
        remaining_edges = target_edge_count - edges_generated
        knows_count = min(remaining_edges, len(persons) * 3)  # 平均每人认识3个人
        
        for _ in range(knows_count):
            person1 = random.choice(persons)
            person2 = random.choice(persons)
            
            if person1["name"] != person2["name"]:  # 避免自环
                since_date = (datetime.now() - timedelta(days=random.randint(30, 3650))).strftime('%Y-%m-%d')
                
                edge = {
                    "type": "knows",
                    "from_label": "Person",
                    "from_name": person1["name"],
                    "to_label": "Person",
                    "to_name": person2["name"],
                    "properties": [("since", f"'{since_date}'")]
                }
                batch_edges.append(edge)
                edges_generated += 1
                
                if len(batch_edges) >= batch_size:
                    self._insert_edges_batch(batch_edges)
                    batch_edges = []
                
                if edges_generated >= target_edge_count:
                    break
        
        # 4. invests_in 关系 (少量投资关系)
        remaining_edges = target_edge_count - edges_generated
        invest_count = min(remaining_edges, len(persons) // 10)  # 10%的人有投资
        
        investors = random.sample(persons, min(invest_count, len(persons)))
        for investor in investors:
            company = random.choice(companies)
            amount = round(random.uniform(10000, 1000000), 2)
            
            edge = {
                "type": "invests_in",
                "from_label": "Person",
                "from_name": investor["name"],
                "to_label": "Company",
                "to_name": company["name"],
                "properties": [("amount", str(amount))]
            }
            batch_edges.append(edge)
            edges_generated += 1
            
            if len(batch_edges) >= batch_size:
                self._insert_edges_batch(batch_edges)
                batch_edges = []
            
            if edges_generated >= target_edge_count:
                break
        
        # 插入剩余的边
        if batch_edges:
            self._insert_edges_batch(batch_edges)
        
        self.edge_count = edges_generated
        print(f"  ✅ 成功生成并插入 {edges_generated} 条边关系\n")
    
    def _insert_edges_batch(self, edges: list):
        """批量插入边"""
        if not edges:
            return
        
        gremlin_parts = []
        for edge in edges:
            props_str = ""
            if edge["properties"]:
                props_list = ", ".join([f"{k}.with({v})" for k, v in edge["properties"]])
                props_str = f".{props_list}"
            
            gremlin_part = (
                f"V('{self._escape_string(edge['from_name'])}').hasLabel('{edge['from_label']}')"
                f".addE('{edge['type']}')"
                f".to(V('{self._escape_string(edge['to_name'])}').hasLabel('{edge['to_label']}'))"
                f"{props_str}"
            )
            gremlin_parts.append(gremlin_part)
        
        # 合并查询
        full_query = "g." + ".next();g.".join(gremlin_parts) + ".next()"
        
        result = self.db.execute_gremlin(full_query)
        if not result["success"]:
            print(f"  ⚠️ 批量插入边失败: {result.get('error', '未知错误')}")
    
    def clear_data(self):
        """清空现有数据（谨慎使用）"""
        print("\n⚠️  警告: 即将清空所有数据！")
        confirm = input("确认清空？(yes/no): ")
        
        if confirm.lower() == "yes":
            print("  🗑️  删除所有边...")
            self.db.execute_gremlin("g.E().drop()")
            
            print("  🗑️  删除所有顶点...")
            self.db.execute_gremlin("g.V().drop()")
            
            print("✅ 数据清空完成！\n")
        else:
            print("❌ 操作已取消\n")
    
    def generate(self, num_persons: int = 500, num_edges: int = 3000, clear_first: bool = False):
        """
        生成完整的测试数据集
        
        Args:
            num_persons: 人物节点数量
            num_edges: 边关系目标数量
            clear_first: 是否先清空数据
        """
        print("=" * 60)
        print("🚀 HugeGraph 测试数据生成器")
        print("=" * 60)
        print(f"配置:")
        print(f"  - 人物节点: {num_persons}")
        print(f"  - 公司节点: {len(self.companies)} (固定)")
        print(f"  - 技能节点: {len(self.skills)} (固定)")
        print(f"  - 边关系: ~{num_edges}")
        print(f"  - 预计总节点数: {num_persons + len(self.companies) + len(self.skills)}")
        print("=" * 60)
        
        # 可选：清空数据
        if clear_first:
            self.clear_data()
        
        # 步骤1: 创建Schema
        self.create_schema()
        
        # 步骤2: 生成数据
        print("📋 步骤2: 生成测试数据...")
        persons = self.generate_persons(num_persons)
        companies = self.generate_companies()
        skills = self.generate_skills()
        print(f"  ✅ 生成 {len(persons)} 个人物")
        print(f"  ✅ 生成 {len(companies)} 个公司")
        print(f"  ✅ 生成 {len(skills)} 个技能\n")
        
        # 步骤3: 插入顶点
        print("📋 步骤3: 插入顶点...")
        self.insert_vertices_batch(persons, "Person")
        self.insert_vertices_batch(companies, "Company")
        self.insert_vertices_batch(skills, "Skill")
        
        # 步骤4: 生成并插入边
        print("📋 步骤4: 生成并插入边关系...")
        self.generate_and_insert_edges(persons, companies, skills, num_edges)
        
        # 步骤5: 验证数据
        print("📋 步骤5: 验证数据...")
        self._verify_data()
        
        # 总结
        print("\n" + "=" * 60)
        print("✅ 测试数据生成完成！")
        print("=" * 60)
        print(f"统计信息:")
        print(f"  - 总顶点数: {self.vertex_count}")
        print(f"  - 总边数: {self.edge_count}")
        print(f"  - 图密度: {self.edge_count / max(self.vertex_count, 1):.2f}")
        print("=" * 60)
        
        # 示例查询
        print("\n💡 可以尝试以下查询测试Agent:")
        print("  1. '找出所有在北京工作的软件工程师'")
        print("  2. '张伟认识哪些人？'")
        print("  3. '阿里巴巴的员工都有哪些技能？'")
        print("  4. '掌握Python和Java的人有哪些？'")
        print("  5. '谁投资了腾讯？投资金额是多少？'")
        print("=" * 60 + "\n")
    
    def _verify_data(self):
        """验证数据完整性"""
        try:
            # 统计顶点
            person_count = self.db.execute_gremlin("g.V().hasLabel('Person').count()")
            company_count = self.db.execute_gremlin("g.V().hasLabel('Company').count()")
            skill_count = self.db.execute_gremlin("g.V().hasLabel('Skill').count()")
            
            # 统计边
            knows_count = self.db.execute_gremlin("g.E().hasLabel('knows').count()")
            works_at_count = self.db.execute_gremlin("g.E().hasLabel('works_at').count()")
            has_skill_count = self.db.execute_gremlin("g.E().hasLabel('has_skill').count()")
            invests_in_count = self.db.execute_gremlin("g.E().hasLabel('invests_in').count()")
            
            print(f"  📊 顶点统计:")
            print(f"     - Person: {person_count['data'][0] if person_count['success'] and person_count['data'] else 0}")
            print(f"     - Company: {company_count['data'][0] if company_count['success'] and company_count['data'] else 0}")
            print(f"     - Skill: {skill_count['data'][0] if skill_count['success'] and skill_count['data'] else 0}")
            
            print(f"  📊 边统计:")
            print(f"     - knows: {knows_count['data'][0] if knows_count['success'] and knows_count['data'] else 0}")
            print(f"     - works_at: {works_at_count['data'][0] if works_at_count['success'] and works_at_count['data'] else 0}")
            print(f"     - has_skill: {has_skill_count['data'][0] if has_skill_count['success'] and has_skill_count['data'] else 0}")
            print(f"     - invests_in: {invests_in_count['data'][0] if invests_in_count['success'] and invests_in_count['data'] else 0}")
            
            total_vertices = sum([
                person_count['data'][0] if person_count['success'] and person_count['data'] else 0,
                company_count['data'][0] if company_count['success'] and company_count['data'] else 0,
                skill_count['data'][0] if skill_count['success'] and skill_count['data'] else 0
            ])
            
            total_edges = sum([
                knows_count['data'][0] if knows_count['success'] and knows_count['data'] else 0,
                works_at_count['data'][0] if works_at_count['success'] and works_at_count['data'] else 0,
                has_skill_count['data'][0] if has_skill_count['success'] and has_skill_count['data'] else 0,
                invests_in_count['data'][0] if invests_in_count['success'] and invests_in_count['data'] else 0
            ])
            
            print(f"\n  ✅ 总计: {total_vertices} 个顶点, {total_edges} 条边")
            
        except Exception as e:
            print(f"  ⚠️ 验证失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="HugeGraph测试数据生成器")
    parser.add_argument("--vertices", type=int, default=500, help="人物节点数量 (默认: 500)")
    parser.add_argument("--edges", type=int, default=3000, help="边关系目标数量 (默认: 3000)")
    parser.add_argument("--clear", action="store_true", help="生成前先清空数据")
    
    args = parser.parse_args()
    
    try:
        # 初始化数据库连接
        print("🔌 连接HugeGraph数据库...")
        db = HugeGraphDB()
        
        if not db.test_connection():
            print("❌ 数据库连接失败，请检查配置")
            sys.exit(1)
        
        print("✅ 数据库连接成功\n")
        
        # 创建生成器并执行
        generator = TestDataGenerator(db)
        generator.generate(
            num_persons=args.vertices,
            num_edges=args.edges,
            clear_first=args.clear
        )
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
