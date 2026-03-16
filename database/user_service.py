from __future__ import annotations

from typing import Optional, Tuple

from werkzeug.security import generate_password_hash, check_password_hash

from .db import execute, init_db


def create_user(username: str, password: str, role: str) -> bool:
    """
    创建用户，返回是否成功。
    role: 'student' 或 'teacher'
    """
    if role not in ("student", "teacher"):
        return False

    init_db()

    password_hash = generate_password_hash(password)
    try:
        execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )
        return True
    except Exception:
        # 可能是唯一约束冲突等
        return False


def get_user_by_username(username: str) -> Optional[Tuple]:
    row = execute(
        "SELECT id, username, password_hash, role FROM users WHERE username = ?",
        (username,),
        fetchone=True,
    )
    return row  # type: ignore[return-value]


def verify_user(username: str, password: str) -> Optional[Tuple[int, str, str]]:
    """
    校验用户名密码，返回 (id, username, role) 或 None。
    """
    row = get_user_by_username(username)
    if not row:
        return None

    user_id, uname, password_hash, role = row
    if not check_password_hash(password_hash, password):
        return None

    return int(user_id), str(uname), str(role)

