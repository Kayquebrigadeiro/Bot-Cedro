"""Camada de dados do bot CEDRO.

Suporta SQLite (local) e PostgreSQL (Supabase/Render).
"""

import os
import re
import sqlite3
from contextlib import contextmanager

from config import DATABASE_URL, DB_FILE

# Tenta usar PostgreSQL se DATABASE_URL estiver configurada
USE_POSTGRES = bool(DATABASE_URL)


def _parse_postgres_url(url: str) -> dict:
    """Parse PostgreSQL URL para componentes."""
    match = re.match(r'postgres(?:ql)?://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/(\w+)', url)
    if match:
        return {
            'user': match.group(1),
            'password': match.group(2),
            'host': match.group(3),
            'port': int(match.group(4)) if match.group(4) else 5432,
            'database': match.group(5)
        }
    raise ValueError(f"DATABASE_URL inválida. Use formato: postgresql://user:pass@host:port/dbname. Sua URL: {url}")


def _conn_sqlite() -> sqlite3.Connection:
    con = sqlite3.connect(DB_FILE, timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA journal_mode = WAL")
    con.execute("PRAGMA busy_timeout = 30000")
    return con


def _conn_postgres():
    """Conecta ao PostgreSQL usando psycopg2."""
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    config = _parse_postgres_url(DATABASE_URL)
    con = psycopg2.connect(
        user=config['user'],
        password=config['password'],
        host=config['host'],
        port=config['port'],
        database=config['database']
    )
    return con


def _conn():
    """Retorna conexão SQLite ou PostgreSQL."""
    if USE_POSTGRES:
        return _conn_postgres()
    return _conn_sqlite()


@contextmanager
def connect():
    con = _conn()
    try:
        yield con
        if USE_POSTGRES:
            con.commit()
        else:
            con.commit()
    finally:
        con.close()


def _column_exists_sqlite(con, table, column):
    return any(row["name"] == column for row in con.execute(f"PRAGMA table_info({table})").fetchall())


def _column_exists_postgres(con, table, column):
    query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = %s AND column_name = %s
    """
    cursor = con.cursor()
    cursor.execute(query, (table, column))
    return cursor.fetchone() is not None


def _column_exists(con, table, column):
    if USE_POSTGRES:
        return _column_exists_postgres(con, table, column)
    return _column_exists_sqlite(con, table, column)


def init() -> None:
    """Cria e migra as tabelas necessárias."""
    with connect() as con:
        if USE_POSTGRES:
            # Tabelas para PostgreSQL
            con.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id      BIGINT PRIMARY KEY,
                    name    TEXT,
                    joined  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS ebooks (
                    id          SERIAL PRIMARY KEY,
                    title       TEXT NOT NULL,
                    description TEXT,
                    file_id     TEXT NOT NULL,
                    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS podcasts (
                    id          SERIAL PRIMARY KEY,
                    title       TEXT NOT NULL,
                    description TEXT,
                    file_id     TEXT NOT NULL,
                    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id         SERIAL PRIMARY KEY,
                    title      TEXT NOT NULL,
                    date_str   TEXT NOT NULL,
                    link       TEXT NOT NULL,
                    date_ts    BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS access_log (
                    id         SERIAL PRIMARY KEY,
                    user_id    BIGINT,
                    item_type  TEXT,
                    item_id    INTEGER,
                    accessed   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Índices
            con.execute("CREATE INDEX IF NOT EXISTS idx_ebooks_created ON ebooks(created_at DESC)")
            con.execute("CREATE INDEX IF NOT EXISTS idx_podcasts_created ON podcasts(created_at DESC)")
            con.execute("CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date_ts ASC, id DESC)")
            con.execute("CREATE INDEX IF NOT EXISTS idx_access_log_item ON access_log(item_type, item_id)")
            con.execute("CREATE INDEX IF NOT EXISTS idx_access_log_user ON access_log(user_id)")
            
            # Adiciona coluna date_ts se não existir
            if not _column_exists(con, "sessions", "date_ts"):
                con.execute("ALTER TABLE sessions ADD COLUMN date_ts BIGINT")
        else:
            # Tabelas para SQLite
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
        if USE_POSTGRES:
            con.execute(
                """
                INSERT INTO users (id, name) VALUES (%s, %s)
                ON CONFLICT(id) DO UPDATE SET name = EXCLUDED.name
                """,
                (user_id, name)
            )
        else:
            con.execute(
                """
                INSERT INTO users (id, name) VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE SET name = excluded.name
                """,
                (user_id, name),
            )


def list_users() -> list[int]:
    with connect() as con:
        if USE_POSTGRES:
            return [row["id"] for row in con.execute("SELECT id FROM users").fetchall()]
        return [row["id"] for row in con.execute("SELECT id FROM users").fetchall()]


def add_ebook(title: str, description: str, file_id: str) -> None:
    with connect() as con:
        if USE_POSTGRES:
            con.execute(
                "INSERT INTO ebooks (title, description, file_id) VALUES (%s, %s, %s)",
                (title, description, file_id),
            )
        else:
            con.execute(
                "INSERT INTO ebooks (title, description, file_id) VALUES (?, ?, ?)",
                (title, description, file_id),
            )


def list_ebooks() -> list[dict]:
    with connect() as con:
        if USE_POSTGRES:
            rows = con.execute("SELECT * FROM ebooks ORDER BY created_at DESC, id DESC").fetchall()
        else:
            rows = con.execute("SELECT * FROM ebooks ORDER BY created_at DESC, id DESC").fetchall()
        return [dict(row) for row in rows]


def get_ebook(ebook_id: int) -> dict | None:
    with connect() as con:
        if USE_POSTGRES:
            row = con.execute("SELECT * FROM ebooks WHERE id = %s", (ebook_id,)).fetchone()
        else:
            row = con.execute("SELECT * FROM ebooks WHERE id = ?", (ebook_id,)).fetchone()
        return dict(row) if row else None


def delete_ebook(ebook_id: int) -> None:
    with connect() as con:
        if USE_POSTGRES:
            con.execute("DELETE FROM ebooks WHERE id = %s", (ebook_id,))
        else:
            con.execute("DELETE FROM ebooks WHERE id = ?", (ebook_id,))


def add_podcast(title: str, description: str, file_id: str) -> None:
    with connect() as con:
        if USE_POSTGRES:
            con.execute(
                "INSERT INTO podcasts (title, description, file_id) VALUES (%s, %s, %s)",
                (title, description, file_id),
            )
        else:
            con.execute(
                "INSERT INTO podcasts (title, description, file_id) VALUES (?, ?, ?)",
                (title, description, file_id),
            )


def list_podcasts() -> list[dict]:
    with connect() as con:
        if USE_POSTGRES:
            rows = con.execute("SELECT * FROM podcasts ORDER BY created_at DESC, id DESC").fetchall()
        else:
            rows = con.execute("SELECT * FROM podcasts ORDER BY created_at DESC, id DESC").fetchall()
        return [dict(row) for row in rows]


def get_podcast(podcast_id: int) -> dict | None:
    with connect() as con:
        if USE_POSTGRES:
            row = con.execute("SELECT * FROM podcasts WHERE id = %s", (podcast_id,)).fetchone()
        else:
            row = con.execute("SELECT * FROM podcasts WHERE id = ?", (podcast_id,)).fetchone()
        return dict(row) if row else None


def delete_podcast(podcast_id: int) -> None:
    with connect() as con:
        if USE_POSTGRES:
            con.execute("DELETE FROM podcasts WHERE id = %s", (podcast_id,))
        else:
            con.execute("DELETE FROM podcasts WHERE id = ?", (podcast_id,))


def add_session(title: str, date_str: str, link: str, date_ts: int | None = None) -> None:
    with connect() as con:
        if USE_POSTGRES:
            con.execute(
                "INSERT INTO sessions (title, date_str, link, date_ts) VALUES (%s, %s, %s, %s)",
                (title, date_str, link, date_ts),
            )
        else:
            con.execute(
                "INSERT INTO sessions (title, date_str, link, date_ts) VALUES (?, ?, ?, ?)",
                (title, date_str, link, date_ts),
            )


def list_sessions() -> list[dict]:
    with connect() as con:
        if USE_POSTGRES:
            rows = con.execute(
                """
                SELECT * FROM sessions
                ORDER BY
                    CASE WHEN date_ts IS NULL THEN 1 ELSE 0 END,
                    date_ts ASC,
                    id DESC
                """
            ).fetchall()
        else:
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
        if USE_POSTGRES:
            con.execute("DELETE FROM sessions WHERE id = %s", (session_id,))
        else:
            con.execute("DELETE FROM sessions WHERE id = ?", (session_id,))


def log_access(user_id: int, item_type: str, item_id: int) -> None:
    with connect() as con:
        if USE_POSTGRES:
            con.execute(
                "INSERT INTO access_log (user_id, item_type, item_id) VALUES (%s, %s, %s)",
                (user_id, item_type, item_id),
            )
        else:
            con.execute(
                "INSERT INTO access_log (user_id, item_type, item_id) VALUES (?, ?, ?)",
                (user_id, item_type, item_id),
            )


def get_stats() -> dict:
    with connect() as con:
        if USE_POSTGRES:
            return {
                "users": con.execute("SELECT COUNT(*) FROM users").fetchone()[0],
                "ebooks": con.execute("SELECT COUNT(*) FROM ebooks").fetchone()[0],
                "podcasts": con.execute("SELECT COUNT(*) FROM podcasts").fetchone()[0],
                "sessions": con.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],
                "accesses": con.execute("SELECT COUNT(*) FROM access_log").fetchone()[0],
            }
        return {
            "users": con.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "ebooks": con.execute("SELECT COUNT(*) FROM ebooks").fetchone()[0],
            "podcasts": con.execute("SELECT COUNT(*) FROM podcasts").fetchone()[0],
            "sessions": con.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],
            "accesses": con.execute("SELECT COUNT(*) FROM access_log").fetchone()[0],
        }
