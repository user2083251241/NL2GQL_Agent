# -*- coding: utf-8 -*-
"""
读取top_rated_movies.csv中的movieId，根据movieId筛选edge_genre.csv中的genre，
并以csv格式存储在experiment中
"""

import pandas as pd
import os

def filter_top_rated_genres():
    """筛选评分为5的电影对应的genre"""
    # 输入文件路径
    top_rated_file = "top_rated_movies.csv"
    genre_file = "../ml-latest-small/hugegraph_data/edge_genre.csv"
    
    # 输出文件路径
    output_file = "top_rated_movies_genres.csv"
    
    print(f"正在读取评分最高的电影ID文件: {top_rated_file}")
    print(f"正在读取电影类型文件: {genre_file}")
    
    # 读取评分最高的电影ID
    top_rated_df = pd.read_csv(top_rated_file)
    
    # 读取电影类型数据
    genre_df = pd.read_csv(genre_file)
    
    print(f"找到 {len(top_rated_df)} 部评分最高的电影")
    print(f"电影类型数据包含 {len(genre_df)} 条记录")
    
    # 将movieId转换为集合以提高查找效率
    top_rated_movie_ids = set(top_rated_df['movieId'])
    
    # 筛选出评分最高的电影的genre
    filtered_genres_df = genre_df[genre_df['movieId'].isin(top_rated_movie_ids)]
    
    print(f"筛选出 {len(filtered_genres_df)} 条评分最高电影的类型记录")
    print(f"涉及 {filtered_genres_df['movieId'].nunique()} 部不同的电影")
    
    # 保存为CSV文件
    filtered_genres_df.to_csv(output_file, index=False)
    
    print(f"结果已保存到: {output_file}")
    
    # 显示前10条记录
    print("前10条记录:")
    print(filtered_genres_df.head(10))
    
    # 显示类型统计
    print("\n类型统计 (前10个最常见类型):")
    genre_counts = filtered_genres_df['genre'].value_counts().head(10)
    print(genre_counts)

if __name__ == "__main__":
    # 确保在experiment目录下运行
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    filter_top_rated_genres()