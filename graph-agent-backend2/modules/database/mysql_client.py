'''
MySQL数据库模块，客户端封装
'''
import mysql.connector
from mysql.connector import Error
from config import Config
from typing import Dict, Any

class MySQLDB:
    '''
    单例模式
    '''

    _instance = None

    def __new__(cls):
        '''单例模式实现'''
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        '''初始化数据库连接'''
        if self._initialized:
            return
        
        try:
            self.connection = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DATABASE,
                charset=Config.MYSQL_CHARSET,
                autocommit=True
            )

            if self.connection.is_connected():
                self._initialized = True
                print(f"✅ MySQL数据库连接成功:{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DATABASE}")
            else:
                raise Exception("MySQL连接失败")
            
        except Error as e:
            print(f"❌ MySQL数据库连接失败: {e}")
            raise

    def execute_query(self, query: str, params: tuple = None) -> Dict[str, Any]:
        '''
        执行SQL查询

        Args:
            query: SQL查询语句
            params: 查询参数元组

            Returns:
                包含查询结果的字典：
                {
                    "success":bool,
                    "data":list,
                    "error":str(可选)
                }
        '''
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchall()

            return {
                "success": True,
                "data": result
            }
        except Error as e:
            error_msg = str(e)
            print(f"❌ MySQL执行错误: {error_msg}")
            print(f"    查询语句：{query}")

            return {
                "success": False,
                "data": [],
                "error": error_msg
            }
        finally:
            if cursor:
                cursor.clone()



def get_mysql_db() -> MySQLDB:
    '''获取MySQL数据库单例实例'''
    return MySQLDB()