import sqlite3
import os
import json

from config import DATABASE_PATH


def get_connection():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    return sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Foydalanuvchilar
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pending_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_telegram_id INTEGER NOT NULL,
            payload TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def create_pending_post(user_telegram_id: int, payload: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pending_posts (user_telegram_id, payload) VALUES (?, ?)",
        (user_telegram_id, json.dumps(payload, ensure_ascii=False))
    )
    post_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return post_id


def get_pending_post(post_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_telegram_id, payload, status FROM pending_posts WHERE id = ?",
        (post_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "user_telegram_id": row[0],
        "payload": json.loads(row[1]),
        "status": row[2]
    }


def list_pending_posts() -> list[int]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM pending_posts WHERE status = 'pending' ORDER BY id")
    post_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return post_ids


def update_pending_post_status(post_id: int, status: str, expected: str = "pending") -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE pending_posts SET status = ? WHERE id = ? AND status = ?",
        (status, post_id, expected)
    )
    updated = cursor.rowcount == 1
    conn.commit()
    conn.close()
    return updated


def add_user(
    telegram_id: int,
    username: str | None,
    first_name: str | None,
    last_name: str | None
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users (
            telegram_id,
            username,
            first_name,
            last_name
        )
        VALUES (?, ?, ?, ?)
    """, (
        telegram_id,
        username,
        first_name,
        last_name
    ))

    # Agar foydalanuvchi oldin mavjud bo'lsa,
    # username/name ma'lumotlarini yangilaymiz.
    cursor.execute("""
        UPDATE users
        SET
            username = ?,
            first_name = ?,
            last_name = ?
        WHERE telegram_id = ?
    """, (
        username,
        first_name,
        last_name,
        telegram_id
    ))

    conn.commit()
    conn.close()
