# -*- coding: utf-8 -*-
"""
筛选评分为5的所有电影，根据movieId去重，以csv格式存储
"""

import pandas as pd
import os

def filter_top_rated_movies():
    """筛选评分为5的电影并去重"""
    # 输入文件路径
    input_file = "../ml-latest-small/hugegraph_data/edge_rating.csv"
    
    # 输出文件路径
    output_file = "top_rated_movies.csv"
    
    print(f"正在读取评分数据文件: {input_file}")
    
    # 读取CSV文件
    df = pd.read_csv(input_file)
    
    # 筛选出评分为5.0的记录
    top_rated_df = df[df['rating'] == 5.0]
    
    print(f"找到 {len(top_rated_df)} 条评分为5的记录")
    
    # 根据movieId去重，保留第一条记录
    unique_movies_df = top_rated_df.drop_duplicates(subset=['movieId'], keep='first')
    
    print(f"去重后得到 {len(unique_movies_df)} 部不同的电影")
    
    # 只保留movieId列（如果需要其他信息可以调整）
    result_df = unique_movies_df[['movieId']].copy()
    
    # 保存为CSV文件
    result_df.to_csv(output_file, index=False)
    
    print(f"结果已保存到: {output_file}")
    print("前10部电影:")
    print(result_df.head(10))

if __name__ == "__main__":
    # 确保在experiment目录下运行
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    filter_top_rated_movies()
