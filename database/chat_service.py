from __future__ import annotations

from typing import Any, List, Tuple

from .db import execute, init_db


def save_chat(question: str, answer: str) -> None:
    """
    保存一轮对话。
    """
    init_db()  # 确保表已创建（幂等操作，成本很低）
    execute(
        "INSERT INTO chat_history (question, answer) VALUES (?, ?)",
        (question, answer),
    )


def get_recent_chats(limit: int = 20) -> List[Tuple[Any, ...]]:
    """
    获取最近的若干条对话记录，按时间倒序。
    """
    rows = execute(
        """
        SELECT id, question, answer, created_at
        FROM chat_history
        ORDER BY created_at DESC, id DESC
        LIMIT ?
        """,
        (limit,),
        fetchall=True,
    )
    return list(rows or [])


def get_all_chats() -> List[Tuple[Any, ...]]:
    """
    获取所有对话记录。
    """
    rows = execute(
        """
        SELECT id, question, answer, created_at
        FROM chat_history
        ORDER BY id ASC
        """,
        fetchall=True,
    )
    return list(rows or [])


def clear_chats() -> None:
    """
    清空所有聊天记录。
    """
    execute("DELETE FROM chat_history", ())

