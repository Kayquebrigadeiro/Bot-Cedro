"""Camada de dados do bot CEDRO usando PostgreSQL (Supabase)."""

import os
import psycopg2
from contextlib import contextmanager

# Pega a DATABASE_URL do ambiente
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não configurada. Configure a variável de ambiente DATABASE_URL.")


@contextmanager
def connect():
    """Conecta ao PostgreSQL."""
    con = psycopg2.connect(DATABASE_URL)
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init() -> None:
    """Inicializa o banco de dados (testa conexão)."""
    try:
        with connect() as con:
            cursor = con.cursor()
            cursor.execute("SELECT 1")
            print("✓ Conexão com banco OK")
    except Exception as e:
        print(f"✗ Erro ao conectar no banco: {e}")
        raise


def register_user(user_id: int, name: str) -> None:
    """Registra ou atualiza um usuário."""
    with connect() as con:
        cursor = con.cursor()
        cursor.execute(
            """
            INSERT INTO users (id, name) VALUES (%s, %s)
            ON CONFLICT(id) DO UPDATE SET name = EXCLUDED.name
            """,
            (user_id, name)
        )


def list_users() -> list[int]:
    """Lista todos os IDs de usuários."""
    with connect() as con:
        cursor = con.cursor()
        cursor.execute("SELECT id FROM users")
        return [row[0] for row in cursor.fetchall()]


def add_ebook(title: str, description: str, file_id: str) -> None:
    """Adiciona um novo eBook."""
    with connect() as con:
        cursor = con.cursor()
        cursor.execute(
            "INSERT INTO ebooks (title, description, file_id) VALUES (%s, %s, %s)",
            (title, description, file_id)
        )


def list_ebooks() -> list[dict]:
    """Lista todos os eBooks."""
    with connect() as con:
        cursor = con.cursor()
        cursor.execute("SELECT id, title, description, file_id, created_at FROM ebooks ORDER BY created_at DESC")
        return [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "file_id": row[3],
                "created_at": row[4]
            }
            for row in cursor.fetchall()
        ]


def get_ebook(ebook_id: int) -> dict | None:
    """Busca um eBook por ID."""
    with connect() as con:
        cursor = con.cursor()
        cursor.execute("SELECT id, title, description, file_id, created_at FROM ebooks WHERE id = %s", (ebook_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "file_id": row[3],
                "created_at": row[4]
            }
        return None


def delete_ebook(ebook_id: int) -> None:
    """Remove um eBook."""
    with connect() as con:
        cursor = con.cursor()
        cursor.execute("DELETE FROM ebooks WHERE id = %s", (ebook_id,))


def add_podcast(title: str, description: str, file_id: str) -> None:
    """Adiciona um novo podcast."""
    with connect() as con:
        cursor = con.cursor()
        cursor.execute(
            "INSERT INTO podcasts (title, description, file_id) VALUES (%s, %s, %s)",
            (title, description, file_id)
        )


def list_podcasts() -> list[dict]:
    """Lista todos os podcasts."""
    with connect() as con:
        cursor = con.cursor()
        cursor.execute("SELECT id, title, description, file_id, created_at FROM podcasts ORDER BY created_at DESC")
        return [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "file_id": row[3],
                "created_at": row[4]
            }
            for row in cursor.fetchall()
        ]


def get_podcast(podcast_id: int) -> dict | None:
    """Busca um podcast por ID."""
    with connect() as con:
        cursor = con.cursor()
        cursor.execute("SELECT id, title, description, file_id, created_at FROM podcasts WHERE id = %s", (podcast_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "file_id": row[3],
                "created_at": row[4]
            }
        return None


def delete_podcast(podcast_id: int) -> None:
    """Remove um podcast."""
    with connect() as con:
        cursor = con.cursor()
        cursor.execute("DELETE FROM podcasts WHERE id = %s", (podcast_id,))


def add_session(title: str, date_str: str, link: str, date_ts: int | None = None) -> None:
    """Adiciona uma nova sessão."""
    with connect() as con:
        cursor = con.cursor()
        cursor.execute(
            "INSERT INTO sessions (title, date_str, link, date_ts) VALUES (%s, %s, %s, %s)",
            (title, date_str, link, date_ts)
        )


def list_sessions() -> list[dict]:
    """Lista todas as sessões."""
    with connect() as con:
        cursor = con.cursor()
        cursor.execute(
            """
            SELECT id, title, date_str, link, date_ts, created_at 
            FROM sessions
            ORDER BY
                CASE WHEN date_ts IS NULL THEN 1 ELSE 0 END,
                date_ts ASC,
                id DESC
            """
        )
        return [
            {
                "id": row[0],
                "title": row[1],
                "date_str": row[2],
                "link": row[3],
                "date_ts": row[4],
                "created_at": row[5]
            }
            for row in cursor.fetchall()
        ]


def delete_session(session_id: int) -> None:
    """Remove uma sessão."""
    with connect() as con:
        cursor = con.cursor()
        cursor.execute("DELETE FROM sessions WHERE id = %s", (session_id,))


def log_access(user_id: int, item_type: str, item_id: int) -> None:
    """Registra um acesso."""
    with connect() as con:
        cursor = con.cursor()
        cursor.execute(
            "INSERT INTO access_log (user_id, item_type, item_id) VALUES (%s, %s, %s)",
            (user_id, item_type, item_id)
        )


def get_stats() -> dict:
    """Retorna estatísticas."""
    with connect() as con:
        cursor = con.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM ebooks")
        ebooks = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM podcasts")
        podcasts = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM sessions")
        sessions = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM access_log")
        accesses = cursor.fetchone()[0]
        
        return {
            "users": users,
            "ebooks": ebooks,
            "podcasts": podcasts,
            "sessions": sessions,
            "accesses": accesses,
        }
