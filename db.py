"""
db.py — Camada de dados do bot CEDRO
Utiliza SQLite (sem dependências externas além do Python padrão)
"""

import sqlite3
from config import DB_FILE


def _conn():
    c = sqlite3.connect(DB_FILE)
    c.row_factory = sqlite3.Row
    return c


def init():
    """Cria as tabelas se não existirem."""
    with _conn() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id      INTEGER PRIMARY KEY,
                name    TEXT,
                joined  TEXT DEFAULT (datetime('now','localtime'))
            );

            CREATE TABLE IF NOT EXISTS ebooks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                description TEXT,
                file_id     TEXT NOT NULL,
                created_at  TEXT DEFAULT (datetime('now','localtime'))
            );

            CREATE TABLE IF NOT EXISTS podcasts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                description TEXT,
                file_id     TEXT NOT NULL,
                created_at  TEXT DEFAULT (datetime('now','localtime'))
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                title    TEXT NOT NULL,
                date_str TEXT NOT NULL,
                link     TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now','localtime'))
            );

            CREATE TABLE IF NOT EXISTS access_log (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER,
                item_type  TEXT,
                item_id    INTEGER,
                accessed   TEXT DEFAULT (datetime('now','localtime'))
            );
        """)


# ── Usuários ──────────────────────────────────────────────────────────────────

def register_user(user_id: int, name: str):
    with _conn() as con:
        con.execute(
            "INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)",
            (user_id, name)
        )


def list_users() -> list[int]:
    with _conn() as con:
        return [r["id"] for r in con.execute("SELECT id FROM users").fetchall()]


# ── eBooks ────────────────────────────────────────────────────────────────────

def add_ebook(title: str, description: str, file_id: str):
    with _conn() as con:
        con.execute(
            "INSERT INTO ebooks (title, description, file_id) VALUES (?, ?, ?)",
            (title, description, file_id)
        )


def list_ebooks() -> list[dict]:
    with _conn() as con:
        return [dict(r) for r in con.execute("SELECT * FROM ebooks ORDER BY id DESC").fetchall()]


def get_ebook(ebook_id: int) -> dict | None:
    with _conn() as con:
        r = con.execute("SELECT * FROM ebooks WHERE id = ?", (ebook_id,)).fetchone()
        return dict(r) if r else None


def delete_ebook(ebook_id: int):
    with _conn() as con:
        con.execute("DELETE FROM ebooks WHERE id = ?", (ebook_id,))


# ── Podcasts ──────────────────────────────────────────────────────────────────

def add_podcast(title: str, description: str, file_id: str):
    with _conn() as con:
        con.execute(
            "INSERT INTO podcasts (title, description, file_id) VALUES (?, ?, ?)",
            (title, description, file_id)
        )


def list_podcasts() -> list[dict]:
    with _conn() as con:
        return [dict(r) for r in con.execute("SELECT * FROM podcasts ORDER BY id DESC").fetchall()]


def get_podcast(podcast_id: int) -> dict | None:
    with _conn() as con:
        r = con.execute("SELECT * FROM podcasts WHERE id = ?", (podcast_id,)).fetchone()
        return dict(r) if r else None


def delete_podcast(podcast_id: int):
    with _conn() as con:
        con.execute("DELETE FROM podcasts WHERE id = ?", (podcast_id,))


# ── Sessões ───────────────────────────────────────────────────────────────────

def add_session(title: str, date_str: str, link: str):
    with _conn() as con:
        con.execute(
            "INSERT INTO sessions (title, date_str, link) VALUES (?, ?, ?)",
            (title, date_str, link)
        )


def list_sessions() -> list[dict]:
    with _conn() as con:
        return [dict(r) for r in con.execute("SELECT * FROM sessions ORDER BY id DESC").fetchall()]


def delete_session(session_id: int):
    with _conn() as con:
        con.execute("DELETE FROM sessions WHERE id = ?", (session_id,))


# ── Log de Acesso ─────────────────────────────────────────────────────────────

def log_access(user_id: int, item_type: str, item_id: int):
    with _conn() as con:
        con.execute(
            "INSERT INTO access_log (user_id, item_type, item_id) VALUES (?, ?, ?)",
            (user_id, item_type, item_id)
        )


# ── Estatísticas ──────────────────────────────────────────────────────────────

def get_stats() -> dict:
    with _conn() as con:
        return {
            "users":    con.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "ebooks":   con.execute("SELECT COUNT(*) FROM ebooks").fetchone()[0],
            "podcasts": con.execute("SELECT COUNT(*) FROM podcasts").fetchone()[0],
            "sessions": con.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],
        }