from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .db import execute


def get_chat_stats() -> Dict[str, Any]:
    """
    获取聊天记录的一些汇总统计信息。

    返回示例：
    {
        "total_chats": 100,
        "first_chat_at": "2025-01-01 10:00:00",
        "last_chat_at": "2025-01-02 11:00:00"
    }
    """
    row = execute(
        """
        SELECT
            COUNT(*) AS total_chats,
            MIN(created_at) AS first_chat_at,
            MAX(created_at) AS last_chat_at
        FROM chat_history
        """,
        fetchone=True,
    )

    total_chats, first_chat_at, last_chat_at = row if row is not None else (0, None, None)

    return {
        "total_chats": total_chats,
        "first_chat_at": first_chat_at,
        "last_chat_at": last_chat_at,
    }


def get_top_questions(limit: int = 10) -> List[Tuple[str, int]]:
    """
    按出现次数统计最常见的问题。

    返回形如 [(question, count), ...]
    """
    rows = execute(
        """
        SELECT
            question,
            COUNT(*) AS cnt
        FROM chat_history
        WHERE question IS NOT NULL AND question != ''
        GROUP BY question
        ORDER BY cnt DESC
        LIMIT ?
        """,
        (limit,),
        fetchall=True,
    )

    if not rows:
        return []

    # 将 Any 转成更具体的类型
    return [(str(q), int(c)) for q, c in rows]

