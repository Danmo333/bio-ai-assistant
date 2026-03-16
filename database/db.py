import sqlite3
from typing import Any, Iterable, Optional

from config import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """
    获取一个到 SQLite 数据库的连接。
    由调用方负责关闭连接（推荐搭配 context manager 使用）。
    """
    return sqlite3.connect(DATABASE_PATH)


def init_db() -> None:
    """
    初始化数据库结构。
    - 聊天记录表 chat_history
    - 用户表 users
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # 1) 创建表（如果不存在）
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question TEXT,
                answer TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password_hash TEXT,
                role TEXT, -- 'student' 或 'teacher'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # 2) 兼容旧库：如果 chat_history 表里还没有 created_at 列，则补一列
        cursor.execute("PRAGMA table_info(chat_history)")
        columns = [row[1] for row in cursor.fetchall()]  # row[1] 是列名
        if "created_at" not in columns:
            cursor.execute(
                "ALTER TABLE chat_history "
                "ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            )
        conn.commit()
    finally:
        conn.close()


def execute(
    sql: str,
    params: Iterable[Any] | None = None,
    *,
    fetchone: bool = False,
    fetchall: bool = False,
) -> Optional[list[tuple[Any, ...]] | tuple[Any, ...]]:
    """
    执行一条 SQL 语句的便捷方法。

    - 自动打开 / 关闭连接
    - 可选择返回单条、多条或不返回数据
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, tuple(params or ()))

        result: Optional[list[tuple[Any, ...]] | tuple[Any, ...]] = None
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()

        conn.commit()
        return result
    finally:
        conn.close()

