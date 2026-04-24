# result = self._client.gremlin().exec(query) 的真实样子
{
    "data": [],       # ✅ 核心：你的查询结果都在这里（列表格式）
    "vertices": [],   # 顶点数据（仅查询顶点时才有）
    "edges": [],      # 边数据（仅查询边时才有）
    "properties": []  # 附属属性（几乎不用）
}

# data 永远是一个列表 []，里面的内容由你的查询语句决定
情况 1：查询标签（如 g.V().label().dedup()）
data = ["Person", "Company", "Product"]  # 标签列表

情况 2：查询顶点 / 边详情（如 elementMap()）
data = [
    {
        "id": 1,                # 顶点ID
        "label": "Person",      # 顶点标签
        "name": "张三",         # 自定义属性
        "age": 20               # 自定义属性
    },
    {
        "id": 2,
        "label": "Person",
        "name": "李四",
        "age": 25
    }
]

情况 3：查询统计（如 g.V().count()）
data = [100]  # 统计结果放在列表里

# 最终 return 的结果，前端调用拿到的格式：
{
    "success": True/False,  # 是否执行成功
    "data": [],             # 就是上面的查询结果列表
    "count": 数字,          # 数据条数
    "error": "错误信息"     # 失败时才有
}