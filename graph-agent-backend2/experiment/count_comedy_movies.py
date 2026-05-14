# -*- coding: utf-8 -*-
"""
统计top_rated_movies_genres.csv中genre为Comedy的电影数量
"""

import pandas as pd
import os

def count_comedy_movies():
    """统计Comedy类型的电影数量"""
    # 输入文件路径
    input_file = "top_rated_movies_genres.csv"
    
    print(f"正在读取文件: {input_file}")
    
    # 读取CSV文件
    df = pd.read_csv(input_file)
    
    # 统计genre为Comedy的记录数量
    comedy_count = len(df[df['genre'] == 'Comedy'])
    
    # 统计包含Comedy的不同电影数量（去重）
    comedy_movies = df[df['genre'] == 'Comedy']['movieId'].nunique()
    
    print(f"genre为'Comedy'的记录总数: {comedy_count}")
    print(f"包含'Comedy'类型的不重复电影数量: {comedy_movies}")
    
    return comedy_count, comedy_movies

if __name__ == "__main__":
    # 确保在experiment目录下运行
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    count_comedy_movies()