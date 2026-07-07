import sqlite3
from typing import Optional

from app.db.connection import get_connection


def count_users() -> int:
    conn = get_connection()
    try:
        row = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()
        return row["count"] if row else 0
    finally:
        conn.close()


def get_user_by_username(username: str):
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
    finally:
        conn.close()


def create_user(username: str, hashed_password: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, hashed_password) VALUES (?, ?)",
            (username, hashed_password),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise
    finally:
        conn.close()
