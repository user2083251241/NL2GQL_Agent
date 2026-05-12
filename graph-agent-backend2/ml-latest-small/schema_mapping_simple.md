# MovieLens 数据库 Schema 简化映射表

## 顶点类型 (Nodes)

### User (用户)
- `userId`: 用户ID

### Movie (电影)  
- `movieId`: 电影ID
- `title`: 电影标题
- `imdbId`: IMDb标识符
- `tmdbId`: TMDB标识符

### Genre (电影类型)
- `name`: 类型名称

## 边类型 (Relationships)

### rated (用户评分)
- 源: User → 目标: Movie
- `rating`: 评分 (0.5-5.0星)
- `timestamp`: 评分时间

### tagged (用户标记)
- 源: User → 目标: Movie  
- `tag`: 标签内容
- `timestamp`: 标记时间

### belongsTo (电影分类)
- 源: Movie → 目标: Genre
- (无属性)

## 字段说明速查

| 字段 | 中文含义 | 所在位置 |
|------|---------|----------|
| userId | 用户ID | User顶点, rated/tagged边源 |
| movieId | 电影ID | Movie顶点, rated/tagged边目标 |
| title | 电影标题 | Movie顶点 |
| imdbId | IMDb ID | Movie顶点 |
| tmdbId | TMDB ID | Movie顶点 |
| name | 类型名称 | Genre顶点 |
| rating | 评分 | rated边属性 |
| timestamp | 时间戳 | rated/tagged边属性 |
| tag | 标签 | tagged边属性 |