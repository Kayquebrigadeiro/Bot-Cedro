"""Configurações do bot CEDRO.

Use variáveis de ambiente no Render:
- BOT_TOKEN ou TELEGRAM_TOKEN
- ADMIN_IDS com IDs separados por vírgula
- DB_FILE opcional (para SQLite local)
- DATABASE_URL (para PostgreSQL no Render)
"""

import os
import re


def _load_dotenv(path: str = ".env") -> None:
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()

TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN") or ""
DB_FILE = os.getenv("DB_FILE", "cedro.db")

# Suporte a PostgreSQL no Render
DATABASE_URL = os.getenv("DATABASE_URL")


def _parse_postgres_url(url: str) -> dict:
    """Parse PostgreSQL URL para componentes."""
    # Tenta formato completo: postgresql://user:pass@host:port/db
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


def _parse_admin_ids(raw_value: str) -> set[int]:
    admin_ids: set[int] = set()
    for item in raw_value.replace(";", ",").split(","):
        item = item.strip()
        if not item:
            continue
        try:
            admin_ids.add(int(item))
        except ValueError as exc:
            raise ValueError(f"ADMIN_IDS contém um ID inválido: {item!r}") from exc
    return admin_ids


ADMIN_IDS = _parse_admin_ids(os.getenv("ADMIN_IDS", "6197047295"))
