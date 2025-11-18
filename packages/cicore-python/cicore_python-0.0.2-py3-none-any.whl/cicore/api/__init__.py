"""
Cicore API模块
包含数据库接口等API功能
"""

from .mongodb import MongoDBManager, mongodb_manager

__all__ = ['MongoDBManager', 'mongodb_manager']