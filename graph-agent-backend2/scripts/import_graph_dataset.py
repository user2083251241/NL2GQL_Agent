"""
开源图数据集导入脚本 - 专门用于向HugeGraph导入开源图数据集

支持的数据集：
1. MovieLens (ml-latest-small) - 用户/电影/标签社交网络
2. DBLP (计算机科学合作网络) - 作者/论文/会议关系
3. Karate Club (空手道俱乐部) - 经典社交网络数据集

使用方式：
    # 导入MovieLens数据集
    python scripts/import_graph_dataset.py --dataset movielens --max-vertices 1000
    
    # 导入DBLP数据集  
    python scripts/import_graph_dataset.py --dataset dblp --max-papers 500
    
    # 导入Karate Club数据集
    python scripts/import_graph_dataset.py --dataset karate
    
    # 清空现有数据并重新导入
    python scripts/import_graph_dataset.py --dataset movielens --clear-first
"""
import sys
import os
import argparse
import requests
import zipfile
import json
import tempfile
from pathlib import Path
import pandas as pd

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.database.client import HugeGraphDB
from config import Config


class GraphDatasetImporter:
    """开源图数据集导入器"""
    
    def __init__(self):
        self.db = None
        
    def initialize_connection(self):
        """初始化HugeGraph连接"""
        try:
            self.db = HugeGraphDB()
            print("✅ HugeGraph连接成功")
        except Exception as e:
            print(f"❌ HugeGraph连接失败: {e}")
            raise
    
    def clear_existing_data(self):
        """清空现有图数据（谨慎使用）"""
        print("⚠️  正在清空现有图数据...")
        try:
            # 删除所有边
            result = self.db.execute_gremlin("g.E().drop().iterate()")
            print("✅ 所有边已删除")
            
            # 删除所有顶点  
            result = self.db.execute_gremlin("g.V().drop().iterate()")
            print("✅ 所有顶点已删除")
            
            # 清空Schema（需要逐个删除）
            schema_info = self.db.get_schema()
            
            # 删除边标签
            for edge_label in schema_info['edge_labels']:
                try:
                    self.db.execute_gremlin(f"schema.edgeLabel('{edge_label}').remove()")
                except:
                    pass
            
            # 删除顶点标签
            for vertex_label in schema_info['vertex_labels']:
                try:
                    self.db.execute_gremlin(f"schema.vertexLabel('{vertex_label}').remove()")
                except:
                    pass
                    
            # 删除属性键
            # 注意：HugeGraph会自动清理未使用的属性键
            
            print("✅ Schema已清空")
            
        except Exception as e:
            print(f"⚠️  清空数据时出现错误: {e}")
    
    def download_and_extract(self, url, filename, extract_dir):
        """下载并解压数据集"""
        print(f"📥 下载数据集: {filename}")
        
        zip_path = os.path.join(extract_dir, filename)
        
        # 下载文件
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # 解压文件
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        print(f"✅ {filename} 下载并解压完成")
        return extract_dir
    
    def import_movielens(self, max_vertices=None):
        """导入MovieLens数据集"""
        print("🎬 开始导入MovieLens数据集...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 下载MovieLens数据集
            url = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
            extract_dir = self.download_and_extract(url, "ml-latest-small.zip", temp_dir)
            data_dir = os.path.join(extract_dir, "ml-latest-small")
            
            # 读取数据文件
            movies_df = pd.read_csv(os.path.join(data_dir, "movies.csv"))
            ratings_df = pd.read_csv(os.path.join(data_dir, "ratings.csv"))
            tags_df = pd.read_csv(os.path.join(data_dir, "tags.csv"))
            
            # 限制数据量
            if max_vertices:
                movies_df = movies_df.head(max_vertices)
                user_ids = set(ratings_df['userId'].unique()) | set(tags_df['userId'].unique())
                user_ids = list(user_ids)[:max_vertices//2] if max_vertices else list(user_ids)
                ratings_df = ratings_df[ratings_df['userId'].isin(user_ids)]
                tags_df = tags_df[tags_df['userId'].isin(user_ids)]
            
            # 创建Schema
            self.create_movielens_schema()
            
            # 导入数据
            self.import_movielens_data(movies_df, ratings_df, tags_df)
        
        print("🎉 MovieLens数据集导入完成！")
    
    def create_movielens_schema(self):
        """创建MovieLens Schema"""
        print("🔧 创建MovieLens Schema...")
        
        # 创建顶点标签
        vertex_labels = ['User', 'Movie']
        for label in vertex_labels:
            try:
                self.db.execute_gremlin(
                    f"schema.vertexLabel('{label}').useAutomaticId().ifNotExist().create()"
                )
                print(f"✅ 顶点标签 {label} 创建成功")
            except Exception as e:
                print(f"⚠️  顶点标签 {label} 创建失败: {e}")
        
        # 创建边标签
        try:
            self.db.execute_gremlin(
                "schema.edgeLabel('RATED').sourceLabel('User').targetLabel('Movie').ifNotExist().create()"
            )
            print("✅ 边标签 RATED 创建成功")
        except Exception as e:
            print(f"⚠️  边标签 RATED 创建失败: {e}")
        
        try:
            self.db.execute_gremlin(
                "schema.edgeLabel('TAGGED').sourceLabel('User').targetLabel('Movie').ifNotExist().create()"
            )
            print("✅ 边标签 TAGGED 创建成功")
        except Exception as e:
            print(f"⚠️  边标签 TAGGED 创建失败: {e}")
        
        # 创建属性键
        properties = ['userId', 'movieId', 'title', 'genres', 'rating', 'timestamp', 'tag']
        for prop in properties:
            try:
                if prop in ['rating', 'timestamp']:
                    self.db.execute_gremlin(
                        f"schema.propertyKey('{prop}').asDouble().ifNotExist().create()"
                    )
                else:
                    self.db.execute_gremlin(
                        f"schema.propertyKey('{prop}').asText().ifNotExist().create()"
                    )
                print(f"✅ 属性键 {prop} 创建成功")
            except Exception as e:
                print(f"⚠️  属性键 {prop} 创建失败: {e}")
        
        # 为顶点标签添加属性
        try:
            self.db.execute_gremlin(
                "schema.vertexLabel('User').properties('userId').alter()"
            )
            self.db.execute_gremlin(
                "schema.vertexLabel('Movie').properties('movieId', 'title', 'genres').alter()"
            )
            print("✅ 顶点属性分配成功")
        except Exception as e:
            print(f"⚠️  顶点属性分配失败: {e}")
    
    def import_movielens_data(self, movies_df, ratings_df, tags_df, batch_size=1000):
        """导入MovieLens数据"""
        print("📤 开始批量导入数据...")
        
        # 批量插入用户顶点
        user_ids = set(ratings_df['userId'].unique()) | set(tags_df['userId'].unique())
        user_vertices = []
        for user_id in list(user_ids):
            user_vertices.append(f"g.addV('User').property('userId', {user_id})")
        
        self.batch_execute_gremlin(user_vertices, batch_size, "用户顶点")
        
        # 批量插入电影顶点
        movie_vertices = []
        for _, row in movies_df.iterrows():
            title = str(row['title']).replace("'", "\\'").replace('"', '\\"')
            genres = str(row['genres']).replace("'", "\\'").replace('"', '\\"')
            movie_vertices.append(
                f"g.addV('Movie')"
                f".property('movieId', {row['movieId']})"
                f".property('title', '{title}')"
                f".property('genres', '{genres}')"
            )
        
        self.batch_execute_gremlin(movie_vertices, batch_size, "电影顶点")
        
        # 批量插入评分边
        rating_edges = []
        for _, row in ratings_df.head(max_vertices).iterrows():
            rating_edges.append(
                f"g.V().has('User', 'userId', {row['userId']})"
                f".addE('RATED')"
                f".to(__.V().has('Movie', 'movieId', {row['movieId']}))"
                f".property('rating', {row['rating']})"
                f".property('timestamp', {row['timestamp']})"
            )
        
        self.batch_execute_gremlin(rating_edges, batch_size, "评分边")
        
        # 批量插入标签边
        tag_edges = []
        for _, row in tags_df.head(max_vertices).iterrows():
            # 处理标签中的特殊字符
            tag = str(row['tag']).replace("'", "\\'")
            tag_edges.append(
                f"g.V().has('User', 'userId', {row['userId']})"
                f".addE('TAGGED')"
                f".to(__.V().has('Movie', 'movieId', {row['movieId']}))"
                f".property('tag', '{tag}')"
                f".property('timestamp', {row['timestamp']})"
            )
        
        self.batch_execute_gremlin(tag_edges, batch_size, "标签边")
    
    def import_dblp(self, max_papers=None):
        """导入DBLP数据集"""
        print("📚 开始导入DBLP数据集...")
        
        # DBLP数据集较大，这里提供简化版本的导入逻辑
        # 实际使用时可以从 https://aminer.org/citation 下载
        
        # 创建DBLP Schema
        self.create_dblp_schema()
        
        # 这里可以添加具体的DBLP数据导入逻辑
        # 由于DBLP数据格式复杂，建议先下载处理好的CSV格式
        
        print("ℹ️  DBLP数据集导入功能待完善，请准备CSV格式的DBLP数据")
        print("   建议数据结构：")
        print("   - authors.csv: author_id, name, affiliation")
        print("   - papers.csv: paper_id, title, year, venue")
        print("   - author_paper.csv: author_id, paper_id")
        print("   - paper_citation.csv: paper_id, cited_paper_id")
    
    def create_dblp_schema(self):
        """创建DBLP Schema"""
        print("🔧 创建DBLP Schema...")
        
        # 创建顶点标签
        labels = ['Author', 'Paper', 'Venue']
        for label in labels:
            try:
                self.db.execute_gremlin(
                    f"schema.vertexLabel('{label}').useAutomaticId().ifNotExist().create()"
                )
                print(f"✅ 顶点标签 {label} 创建成功")
            except Exception as e:
                print(f"⚠️  顶点标签 {label} 创建失败: {e}")
        
        # 创建边标签
        edges = ['WRITES', 'PUBLISHED_IN', 'CITES']
        edge_configs = [
            ("WRITES", "Author", "Paper"),
            ("PUBLISHED_IN", "Paper", "Venue"), 
            ("CITES", "Paper", "Paper")
        ]
        
        for edge_label, source, target in edge_configs:
            try:
                self.db.execute_gremlin(
                    f"schema.edgeLabel('{edge_label}').sourceLabel('{source}').targetLabel('{target}').ifNotExist().create()"
                )
                print(f"✅ 边标签 {edge_label} 创建成功")
            except Exception as e:
                print(f"⚠️  边标签 {edge_label} 创建失败: {e}")
    
    def create_karate_schema(self):
        """在HugeGraph中创建Karate Club Schema"""
        print("🔧 创建Karate Club Schema...")
        
        # 先尝试删除可能存在的旧Schema（避免冲突）
        try:
            self.hugegraph_db.execute_gremlin("schema.propertyKey('id').remove()")
        except:
            pass
        
        try:
            self.hugegraph_db.execute_gremlin("schema.vertexLabel('Person').remove()")
        except:
            pass
            
        try:
            self.hugegraph_db.execute_gremlin("schema.edgeLabel('KNOWS').remove()")
        except:
            pass
        
        # 创建属性键
        try:
            self.hugegraph_db.execute_gremlin(
                "schema.propertyKey('id').asInt().ifNotExist().create()"
            )
            print("✅ 属性键 'id' 创建成功")
        except Exception as e:
            print(f"⚠️ 属性键 'id' 创建失败: {e}")
        
        # 创建顶点标签
        try:
            self.hugegraph_db.execute_gremlin(
                "schema.vertexLabel('Person').properties('id').useCustomizeStringId().ifNotExist().create()"
            )
            print("✅ 顶点标签 'Person' 创建成功")
        except Exception as e:
            print(f"⚠️ 顶点标签 'Person' 创建失败: {e}")
        
        # 创建边标签
        try:
            self.hugegraph_db.execute_gremlin(
                "schema.edgeLabel('KNOWS').sourceLabel('Person').targetLabel('Person').ifNotExist().create()"
            )
            print("✅ 边标签 'KNOWS' 创建成功")
        except Exception as e:
            print(f"⚠️ 边标签 'KNOWS' 创建失败: {e}")

    def import_karate_to_graph(self, nodes, edges):
        """将Karate Club数据导入HugeGraph"""
        print("📤 开始导入Karate Club数据到HugeGraph...")
        
        # 批量插入顶点（使用字符串ID）
        vertex_statements = []
        for node_id in nodes:
            vertex_statements.append(
                f"g.addV('Person').property(T.id, '{node_id}').property('id', {node_id})"
            )
        
        if vertex_statements:
            # 分批执行（每10条一批）
            batch_size = 10
            for i in range(0, len(vertex_statements), batch_size):
                batch = vertex_statements[i:i+batch_size]
                gremlin_query = ";".join(batch)
                result = self.hugegraph_db.execute_gremlin(gremlin_query)
                if result['success']:
                    print(f"✅ 插入 {len(batch)} 个顶点")
                else:
                    print(f"⚠️ 顶点批次 {i//batch_size + 1} 执行失败: {result['error']}")
        
        # 批量插入KNOWS边
        edge_statements = []
        for source, target in edges:
            edge_statements.append(
                f"g.V('{source}').addE('KNOWS').to(__.V('{target}'))"
            )
        
        if edge_statements:
            # 分批执行（每10条一批）
            batch_size = 10
            for i in range(0, len(edge_statements), batch_size):
                batch = edge_statements[i:i+batch_size]
                gremlin_query = ";".join(batch)
                result = self.hugegraph_db.execute_gremlin(gremlin_query)
                if result['success']:
                    print(f"✅ 插入 {len(batch)} 条边")
                else:
                    print(f"⚠️ 边批次 {i//batch_size + 1} 执行失败: {result['error']}")
        
        print("🎉 Karate Club数据导入完成！")
    
    def import_karate(self):
        """导入Karate Club数据集"""
        print("🥋 开始导入Karate Club数据集...")
        
        # Karate Club是经典的社交网络数据集，包含34个成员和78条关系
        # 数据来源: http://konect.cc/networks/ucidata-zachary/
        
        # 创建Schema
        try:
            self.db.execute_gremlin(
                "schema.vertexLabel('Person').useAutomaticId().ifNotExist().create()"
            )
            self.db.execute_gremlin(
                "schema.edgeLabel('KNOWS').sourceLabel('Person').targetLabel('Person').ifNotExist().create()"
            )
            print("✅ Karate Club Schema创建成功")
        except Exception as e:
            print(f"⚠️  Schema创建失败: {e}")
            return
        
        # Karate Club的顶点数据（34个人）
        vertices = []
        for i in range(1, 35):
            vertices.append(f"g.addV('Person').property('id', {i})")
        
        self.batch_execute_gremlin(vertices, 100, "Karate Club顶点")
        
        # Karate Club的边数据（78条关系）
        # 这里只列出部分关系作为示例
        karate_edges = [
            (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 11), (1, 12),
            (1, 13), (1, 14), (1, 18), (1, 20), (1, 22), (1, 32), (2, 3), (2, 4), (2, 8), (2, 14),
            (2, 18), (2, 20), (2, 22), (2, 31), (3, 4), (3, 8), (3, 9), (3, 10), (3, 14), (3, 28),
            (3, 29), (3, 33), (4, 8), (4, 13), (4, 14), (5, 7), (5, 11), (6, 7), (6, 11), (6, 17),
            (7, 17), (8, 30), (8, 32), (8, 33), (9, 33), (10, 34), (14, 34), (15, 33), (15, 34),
            (16, 33), (16, 34), (17, 33), (18, 32), (18, 34), (19, 33), (19, 34), (20, 34), (21, 33),
            (21, 34), (22, 33), (22, 34), (23, 25), (23, 27), (23, 33), (23, 34), (24, 25), (24, 27),
            (24, 33), (24, 34), (25, 32), (26, 33), (26, 34), (27, 33), (27, 34), (28, 34), (29, 32),
            (29, 34), (30, 33), (30, 34), (31, 33), (31, 34), (32, 33), (32, 34), (33, 34)
        ]
        
        edges = []
        for source, target in karate_edges:
            edges.append(
                f"g.V().has('Person', 'id', {source})"
                f".addE('KNOWS')"
                f".to(g.V().has('Person', 'id', {target}))"
            )
        
        self.batch_execute_gremlin(edges, 100, "Karate Club边")
        
        print("🎉 Karate Club数据集导入完成！")
    
    def batch_execute_gremlin(self, queries, batch_size, description):
        """批量执行Gremlin查询"""
        if not queries:
            return
            
        total_batches = (len(queries) + batch_size - 1) // batch_size
        success_count = 0
        
        for i in range(0, len(queries), batch_size):
            batch = queries[i:i+batch_size]
            gremlin_query = ";".join(batch)
            
            try:
                result = self.db.execute_gremlin(gremlin_query)
                if result['success']:
                    success_count += len(batch)
                else:
                    print(f"⚠️  批次 {i//batch_size + 1}/{total_batches} 执行失败: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"⚠️  批次 {i//batch_size + 1}/{total_batches} 执行异常: {e}")
        
        print(f"✅ {description}: {success_count}/{len(queries)} 成功")


def main():
    parser = argparse.ArgumentParser(description='开源图数据集导入工具')
    parser.add_argument('--dataset', choices=['movielens', 'dblp', 'karate'], 
                       required=True, help='选择要导入的数据集')
    parser.add_argument('--max-vertices', type=int, default=1000,
                       help='MovieLens数据集的最大顶点数（默认: 1000）')
    parser.add_argument('--max-papers', type=int, default=500,
                       help='DBLP数据集的最大论文数（默认: 500）')
    parser.add_argument('--clear-first', action='store_true',
                       help='导入前清空现有数据（谨慎使用）')
    
    args = parser.parse_args()
    
    importer = GraphDatasetImporter()
    importer.initialize_connection()
    
    if args.clear_first:
        confirm = input("⚠️  此操作将清空所有现有数据！确认继续吗？(yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ 操作已取消")
            return
        importer.clear_existing_data()
    
    if args.dataset == 'movielens':
        importer.import_movielens(max_vertices=args.max_vertices)
    elif args.dataset == 'dblp':
        importer.import_dblp(max_papers=args.max_papers)
    elif args.dataset == 'karate':
        importer.import_karate()


if __name__ == "__main__":
    main()