import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from modules.database.mysql_client import get_mysql_db

def main():
    print("开始测试数据库连接...")
    print("="*50)

    db = get_mysql_db()

if __name__ == "__main__":
    main()

