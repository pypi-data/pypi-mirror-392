"""
MongoDB数据库管理器
使用public_reader用户进行只读操作
"""

from pymongo.errors import ConnectionFailure, OperationFailure
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class MongoDBManager:
    """MongoDB数据库管理器类"""

    def __init__(self, use_admin=False):
        """初始化MongoDB连接

        :param use_admin: 是否使用管理员用户（用于测试）
        """
        if use_admin:
            pass
        else:
            # 使用新的public_reader用户
            username = "public_reader"
            password = "ioOn7hH2Pbqs0PKT"

            # 构建连接字符串
            self.uri = f"mongodb+srv://{username}:{password}@vanction.i86c0oc.mongodb.net/?appName=Vanction"

        # 创建客户端连接
        self.client = None
        self.is_connected = False

    def connect(self):
        """连接到MongoDB数据库"""
        try:
            # 创建新的客户端并连接到服务器
            self.client = MongoClient(self.uri, server_api=ServerApi('1'))

            # 发送ping命令确认连接成功
            self.client.admin.command('ping')
            self.is_connected = True
            print("成功连接到MongoDB数据库!")
            return True

        except ConnectionFailure as e:
            print(f"连接失败: {e}")
            return False
        except OperationFailure as e:
            print(f"认证失败: {e}")
            return False
        except Exception as e:
            print(f"连接错误: {e}")
            return False

    def disconnect(self):
        """断开数据库连接"""
        if self.client:
            self.client.close()
            self.is_connected = False
            print("已断开MongoDB连接")

    def get_database(self, db_name="test"):
        """获取数据库实例"""
        if not self.is_connected:
            if not self.connect():
                return None

        return self.client[db_name]

    def get_collection(self, db_name, collection_name):
        """获取集合实例"""
        database = self.get_database(db_name)
        if database is not None:
            return database[collection_name]
        return None

    def find_documents(self, db_name, collection_name, query=None, projection=None, limit=100):
        """查询文档"""
        collection = self.get_collection(db_name, collection_name)
        if collection is None:
            return []

        try:
            if query is None:
                query = {}

            cursor = collection.find(query, projection).limit(limit)
            documents = list(cursor)
            return documents

        except OperationFailure as e:
            print(f"查询失败: {e}")
            return []
        except Exception as e:
            print(f"查询错误: {e}")
            return []

    def find_one_document(self, db_name, collection_name, query=None, projection=None):
        """查询单个文档"""
        collection = self.get_collection(db_name, collection_name)
        if collection is None:
            return None

        try:
            if query is None:
                query = {}

            document = collection.find_one(query, projection)
            return document

        except OperationFailure as e:
            print(f"查询失败: {e}")
            return None
        except Exception as e:
            print(f"查询错误: {e}")
            return None

    def count_documents(self, db_name, collection_name, query=None):
        """统计文档数量"""
        collection = self.get_collection(db_name, collection_name)
        if collection is None:
            return 0

        try:
            if query is None:
                query = {}

            count = collection.count_documents(query)
            return count

        except OperationFailure as e:
            print(f"统计失败: {e}")
            return 0
        except Exception as e:
            print(f"统计错误: {e}")
            return 0

    def list_databases(self):
        """列出所有数据库"""
        if not self.is_connected:
            if not self.connect():
                return []

        try:
            databases = self.client.list_database_names()
            return databases

        except OperationFailure as e:
            print(f"获取数据库列表失败: {e}")
            return []
        except Exception as e:
            print(f"获取数据库列表错误: {e}")
            return []

    def get_database_names(self):
        """获取数据库名称列表（list_databases的别名）"""
        return self.list_databases()

    def list_collections(self, db_name):
        """列出指定数据库的所有集合"""
        database = self.get_database(db_name)
        if database is None:
            return []

        try:
            collections = database.list_collection_names()
            return collections

        except OperationFailure as e:
            print(f"获取集合列表失败: {e}")
            return []
        except Exception as e:
            print(f"获取集合列表错误: {e}")
            return []

    def get_collection_names(self, db_name):
        """获取集合名称列表（list_collections的别名）"""
        return self.list_collections(db_name)


# 全局MongoDB管理器实例
mongodb_manager = MongoDBManager()