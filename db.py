"""Camada de dados do bot CEDRO usando SQLite."""

import sqlite3
from contextlib import contextmanager

from config import DB_FILE


def _conn_sqlite() -> sqlite3.Connection:
    con = sqlite3.connect(DB_FILE, timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA journal_mode = WAL")
    con.execute("PRAGMA busy_timeout = 30000")
    return con


@contextmanager
def connect():
    con = _conn_sqlite()
    try:
        yield con
        con.commit()
    finally:
        con.close()


def _column_exists(con, table, column):
    return any(row["name"] == column for row in con.execute(f"PRAGMA table_info({table})").fetchall())


def init() -> None:
    """Cria e migra as tabelas necessárias."""
    with connect() as con:
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
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT NOT NULL,
                date_str   TEXT NOT NULL,
                link       TEXT NOT NULL,
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

        if not _column_exists(con, "sessions", "date_ts"):
            con.execute("ALTER TABLE sessions ADD COLUMN date_ts INTEGER")

        con.executescript("""
            CREATE INDEX IF NOT EXISTS idx_ebooks_created ON ebooks(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_podcasts_created ON podcasts(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date_ts ASC, id DESC);
            CREATE INDEX IF NOT EXISTS idx_access_log_item ON access_log(item_type, item_id);
            CREATE INDEX IF NOT EXISTS idx_access_log_user ON access_log(user_id);
        """)


def register_user(user_id: int, name: str) -> None:
    with connect() as con:
        con.execute(
            """
            INSERT INTO users (id, name) VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET name = excluded.name
            """,
            (user_id, name),
        )


def list_users() -> list[int]:
    with connect() as con:
        return [row["id"] for row in con.execute("SELECT id FROM users").fetchall()]


def add_ebook(title: str, description: str, file_id: str) -> None:
    with connect() as con:
        con.execute(
            "INSERT INTO ebooks (title, description, file_id) VALUES (?, ?, ?)",
            (title, description, file_id),
        )


def list_ebooks() -> list[dict]:
    with connect() as con:
        rows = con.execute("SELECT * FROM ebooks ORDER BY created_at DESC, id DESC").fetchall()
        return [dict(row) for row in rows]


def get_ebook(ebook_id: int) -> dict | None:
    with connect() as con:
        row = con.execute("SELECT * FROM ebooks WHERE id = ?", (ebook_id,)).fetchone()
        return dict(row) if row else None


def delete_ebook(ebook_id: int) -> None:
    with connect() as con:
        con.execute("DELETE FROM ebooks WHERE id = ?", (ebook_id,))


def add_podcast(title: str, description: str, file_id: str) -> None:
    with connect() as con:
        con.execute(
            "INSERT INTO podcasts (title, description, file_id) VALUES (?, ?, ?)",
            (title, description, file_id),
        )


def list_podcasts() -> list[dict]:
    with connect() as con:
        rows = con.execute("SELECT * FROM podcasts ORDER BY created_at DESC, id DESC").fetchall()
        return [dict(row) for row in rows]


def get_podcast(podcast_id: int) -> dict | None:
    with connect() as con:
        row = con.execute("SELECT * FROM podcasts WHERE id = ?", (podcast_id,)).fetchone()
        return dict(row) if row else None


def delete_podcast(podcast_id: int) -> None:
    with connect() as con:
        con.execute("DELETE FROM podcasts WHERE id = ?", (podcast_id,))


def add_session(title: str, date_str: str, link: str, date_ts: int | None = None) -> None:
    with connect() as con:
        con.execute(
            "INSERT INTO sessions (title, date_str, link, date_ts) VALUES (?, ?, ?, ?)",
            (title, date_str, link, date_ts),
        )


def list_sessions() -> list[dict]:
    with connect() as con:
        rows = con.execute(
            """
            SELECT * FROM sessions
            ORDER BY
                CASE WHEN date_ts IS NULL THEN 1 ELSE 0 END,
                date_ts ASC,
                id DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]


def delete_session(session_id: int) -> None:
    with connect() as con:
        con.execute("DELETE FROM sessions WHERE id = ?", (session_id,))


def log_access(user_id: int, item_type: str, item_id: int) -> None:
    with connect() as con:
        con.execute(
            "INSERT INTO access_log (user_id, item_type, item_id) VALUES (?, ?, ?)",
            (user_id, item_type, item_id),
        )


def get_stats() -> dict:
    with connect() as con:
        return {
            "users": con.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "ebooks": con.execute("SELECT COUNT(*) FROM ebooks").fetchone()[0],
            "podcasts": con.execute("SELECT COUNT(*) FROM podcasts").fetchone()[0],
            "sessions": con.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],
            "accesses": con.execute("SELECT COUNT(*) FROM access_log").fetchone()[0],
        }
