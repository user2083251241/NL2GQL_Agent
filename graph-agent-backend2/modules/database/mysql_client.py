'''
MySQL数据库模块，客户端封装
'''
import mysql.connector.pooling
from mysql.connector import Error
from config import Config
from typing import Dict, Any

class MySQLDB:
    '''
    连接池使用单例模式
    功能：
    1. 使用连接池管理数据库连接
    2. 支持高并发下的安全数据库操作
    3. 自动管理连接的获取和归还
    '''

    _instance = None

    def __new__(cls):
        '''单例模式实现'''
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        '''初始化连接池'''
        if self._initialized:
            return
        
        try:
            #连接池配置
            pool_config = {
                'pool_name': 'graph_agent_pool',
                'pool_size': 5,
                'pool_reset_session':True,
                'host': Config.MYSQL_HOST,
                'port': Config.MYSQL_PORT,
                'user': Config.MYSQL_USER,
                'password': Config.MYSQL_PASSWORD,
                'database': Config.MYSQL_DATABASE,
                'charset': Config.MYSQL_CHARSET,
                'autocommit': True,
                'use_unicode': True
            }

            self.pool = mysql.connector.pooling.MySQLConnectionPool(**pool_config)
            self._initialized = True
            print(f"✅ MySQL数据库连接池初始化成功:{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DATABASE}")

        except Error as e:
            print(f"❌ MySQL数据库连接池初始化失败: {e}")
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
        connection = None
        cursor = None
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor(dictionary=True)
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
            if connection:
                connection.close()

        # def get_pool_info(self) -> Dict[str, Any]:
        #     """获取连接池状态信息（用于监控）"""
        #     if hasattr(self, 'pool'):
        #         return {
        #             "pool_name": self.pool.pool_name,
        #             "pool_size": self.pool.pool_size,
        #             "available_connections": len(self.pool._cnx_queue.queue) if hasattr(self.pool._cnx_queue, 'queue') else "unknown"
        #         }
        #     return {"error": "连接池未初始化"}

def get_mysql_db() -> MySQLDB:
    '''获取MySQL数据库单例实例'''
    return MySQLDB()