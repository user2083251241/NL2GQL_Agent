import csv
import os

# 处理 movies.csv：去掉表头，title中的逗号替换为空格
with open('movies.csv', 'r', encoding='utf-8') as f_in, \
     open('movies_clean.csv', 'w', encoding='utf-8', newline='') as f_out:
    reader = csv.reader(f_in)
    writer = csv.writer(f_out, lineterminator='\n')
    next(reader)  # 跳过表头
    for row in reader:
        movie_id = row[0]
        title = row[1].replace(',', ' ')  # 逗号→空格，避免CSV解析错误
        genres = row[2]
        writer.writerow([movie_id, title, genres])

# 处理 ratings.csv：去掉表头，直接复制
with open('ratings.csv', 'r', encoding='utf-8') as f_in, \
     open('ratings_clean.csv', 'w', encoding='utf-8', newline='') as f_out:
    reader = csv.reader(f_in)
    writer = csv.writer(f_out, lineterminator='\n')
    next(reader)  # 跳过表头
    for row in reader:
        writer.writerow(row)

print("预处理完成！")
print("movies_clean.csv 行数:", sum(1 for _ in open('movies_clean.csv', encoding='utf-8')))
print("ratings_clean.csv 行数:", sum(1 for _ in open('ratings_clean.csv', encoding='utf-8')))