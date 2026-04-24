import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from modules.database.client import get_db

def main():
    print("数据库测试")
    print("="*50)

    db = get_db()

    # if db.test_connection():
    #     print("数据库连接成功")
    # else:
    #     print("数据库连接失败")

    result = db.execute_gremlin("g.V().count()")
    
    if result["success"]:
        print(f"当前数据库中顶点数量为: {result['data']}")
    else:
        print(f"查询失败: {result['error']}")

    result = db.execute_gremlin("g.E().count()")
    if result["success"]:
        print(f"当前数据库中边的数量为: {result['data']}")
    else:
        print(f"查询失败: {result['error']}")


    schema = db.get_schema()

    print(f"\n 有{len(schema['vertex_labels'])}类不同的顶点")
    for label in schema['vertex_labels']:
        print(f" - {label}")

    print(f"\n 有{len(schema['edge_labels'])}类不同的边")
    for label in schema['edge_labels']:
        print(f" - {label}")

    print(f"\n 属性信息：")
    for label,props in schema['properties'].items():
        print(f"  {label}: {props}")

    # 可以在 test_db.py 中临时添加这一行来调试
    print("\n",db._client.schema().getEdgeLabels())

    # 执行Gremlin查询所有边，并打印结果
    result = db.execute_gremlin("g.E().valueMap(true)")
    print("\n=== 数据库所有边信息 ===")
    print(result)

    print("\n所有测试完成")
    

if __name__ == "__main__":
    main()