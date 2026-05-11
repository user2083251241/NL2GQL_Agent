# -*- coding: utf-8 -*-
"""
MovieLens -> HugeGraph 数据预处理脚本 (v3)
适用于有表头的标准 MovieLens CSV 文件

用法:
    python preprocess.py
"""
import pandas as pd
import os

BASE_DIR = "."
OUT_DIR = "hugegraph_data"
os.makedirs(OUT_DIR, exist_ok=True)

print("[1/4] 读取原始数据...")

movies  = pd.read_csv(os.path.join(BASE_DIR, "movies.csv"))
links   = pd.read_csv(os.path.join(BASE_DIR, "links.csv"))
ratings = pd.read_csv(os.path.join(BASE_DIR, "ratings.csv"))
tags    = pd.read_csv(os.path.join(BASE_DIR, "tags.csv"))

print(f"    movies:   {len(movies)} 行")
print(f"    links:    {len(links)} 行")
print(f"    ratings:  {len(ratings)} 行")
print(f"    tags:     {len(tags)} 行")

# ---------- 顶点 ----------
print("[2/4] 生成顶点文件...")

# User: 从 ratings 和 tags 中收集所有 userId 去重
users = pd.DataFrame({
    "userId": pd.concat([ratings["userId"], tags["userId"]]).drop_duplicates().sort_values()
})
users.to_csv(os.path.join(OUT_DIR, "vertex_user.csv"), index=False)
print(f"    -> vertex_user.csv   ({len(users)} 用户)")

# Movie: 合并 movies + links，保留 imdbId 前导零（文本类型）
movies_full = movies.merge(links, on="movieId", how="left")
# imdbId 必须保留为字符串，防止丢失前导零（如 0114709）
movies_full["imdbId"] = movies_full["imdbId"].fillna("").astype(str).str.replace(".0", "", regex=False)
movies_full["tmdbId"] = movies_full["tmdbId"].fillna("").astype(str).str.replace(".0", "", regex=False)
movies_full[["movieId", "title", "imdbId", "tmdbId"]].to_csv(
    os.path.join(OUT_DIR, "vertex_movie.csv"), index=False
)
print(f"    -> vertex_movie.csv  ({len(movies_full)} 电影)")

# Genre: 拆分 genres 字段，去重
all_genres = set()
for g_str in movies["genres"].dropna():
    for g in str(g_str).split("|"):
        all_genres.add(g.strip())
genres_df = pd.DataFrame({"name": sorted(all_genres)})
genres_df.to_csv(os.path.join(OUT_DIR, "vertex_genre.csv"), index=False)
print(f"    -> vertex_genre.csv  ({len(genres_df)} 类型)")

# ---------- 边 ----------
print("[3/4] 生成边文件...")

# rated: 用户评分
ratings.to_csv(os.path.join(OUT_DIR, "edge_rating.csv"), index=False)
print(f"    -> edge_rating.csv   ({len(ratings)} 条评分)")

# tagged: 用户标签 (tag 可能包含逗号，pandas 会自动加引号处理)
tags.to_csv(os.path.join(OUT_DIR, "edge_tag.csv"), index=False)
print(f"    -> edge_tag.csv      ({len(tags)} 条标签)")

# belongsTo: 电影-类型关系
genre_edges = []
for _, row in movies.iterrows():
    mid = row["movieId"]
    for g in str(row["genres"]).split("|"):
        genre_edges.append({"movieId": mid, "genre": g.strip()})
pd.DataFrame(genre_edges).to_csv(os.path.join(OUT_DIR, "edge_genre.csv"), index=False)
print(f"    -> edge_genre.csv    ({len(genre_edges)} 条电影-类型关系)")

print("[4/4] 预处理完成！输出目录: ./hugegraph_data/")
print("""
目录结构:
hugegraph_data/
├── vertex_user.csv
├── vertex_movie.csv
├── vertex_genre.csv
├── edge_rating.csv
├── edge_tag.csv
└── edge_genre.csv
""")