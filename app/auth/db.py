import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from ..passwords import hash_password

AUTH_DB_PATH = Path(__file__).resolve().parent.parent / "auth.db"

def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(AUTH_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_auth_db():
    AUTH_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login_at TEXT
            )
            """
        )
        conn.commit()

def get_user_by_login(login: str) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE login = ?", (login,)).fetchone()
        return dict(row) if row else None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

def create_user(login: str, password: str) -> Dict[str, Any]:
    now = datetime.utcnow().isoformat()
    pwd_hash = hash_password(password)
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO users (login, password_hash, created_at) VALUES (?, ?, ?)",
            (login, pwd_hash, now),
        )
        user_id = cur.lastrowid
        conn.commit()
        return {
            "id": user_id,
            "login": login,
            "password_hash": pwd_hash,
            "created_at": now,
            "last_login_at": None,
        }

def update_last_login(user_id: int):
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        conn.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (now, user_id))
        conn.commit()
