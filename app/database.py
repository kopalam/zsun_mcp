"""
数据库连接和配置模块

提供 MySQL 数据库连接和基本的数据库操作功能
"""

import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from contextlib import asynccontextmanager
from typing import Any

logger = logging.getLogger(__name__)

Base = declarative_base()

class TaskORM(Base):
    __tablename__ = 'plugin_smart_tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(255), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(String)
    source_type = Column(String(20))
    status = Column(String(20))
    priority = Column(String(20))
    estimated_duration = Column(Integer)
    deadline = Column(DateTime)
    tags = Column(String(500))
    parent_task_id = Column(Integer)
    agent_origin = Column(String(255))
    is_recurring_template = Column(Boolean, default=False)
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    is_deleted = Column(Boolean, default=False)

class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self):
        # 使用阿里云RDS MySQL配置
        self.host = os.getenv('DB_HOST', 'rm-7xv1g24h1bgmdp0464o.mysql.rds.aliyuncs.com')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.user = os.getenv('DB_USERNAME', 'contract')
        self.password = os.getenv('DB_PASSWORD', 'rapidBuilder!')
        self.database = os.getenv('DB_DATABASE', 'contract')
        self.charset = os.getenv('DB_CHARSET', 'utf8mb4')
    
    def get_url(self):
        return f"mysql+aiomysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?charset={self.charset}"

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self.engine = create_async_engine(self.config.get_url(), echo=False, future=True)
        self.async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
    
    @asynccontextmanager
    async def get_session(self):
        async with self.async_session() as session:
            yield session
    
    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def close(self):
        """关闭数据库连接池"""
        if self.engine:
            try:
                await self.engine.dispose()
                logger.info("数据库连接池已关闭")
            except Exception as e:
                logger.error(f"关闭数据库连接池时出错: {e}")
            finally:
                self.engine = None
    
    async def execute_query(self, query: str, params: tuple = None) -> Any:
        """执行查询语句"""
        try:
            print("[DEBUG] SQL Query:", query)
            print("[DEBUG] SQL Params:", params)
            async with self.get_session() as session:
                result = await session.execute(query, params)
                return result.fetchall()
        except Exception as e:
            logger.error(f"执行查询失败: {e}")
            raise
    
    async def execute_update(self, query: str, params: tuple = None) -> int:
        """执行更新语句"""
        try:
            async with self.get_session() as session:
                result = await session.execute(query, params)
                await session.commit()
                
                # 如果是INSERT语句，返回最后插入的ID
                if query.strip().upper().startswith('INSERT'):
                    return result.lastrowid
                else:
                    return result.rowcount
        except Exception as e:
            logger.error(f"执行更新失败: {e}")
            raise

# 创建全局数据库管理器实例
db_manager = DatabaseManager() 