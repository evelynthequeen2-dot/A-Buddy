"""A-Buddy 本地历史记录存储模块。"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent.parent / "abuddy.sqlite3"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                task_json TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_history(file_name: str, created_at: str, task_data: dict[str, Any]) -> int:
    task_json = json.dumps(task_data, ensure_ascii=False)
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO history (file_name, created_at, task_json) VALUES (?, ?, ?)",
            (file_name, created_at, task_json),
        )
        conn.commit()
        return int(cursor.lastrowid)


def list_history() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, file_name, created_at, task_json FROM history ORDER BY datetime(created_at) DESC, id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def get_history_item(history_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, file_name, created_at, task_json FROM history WHERE id = ?",
            (history_id,),
        ).fetchone()
    return dict(row) if row else None
