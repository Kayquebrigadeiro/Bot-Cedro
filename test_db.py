"""Testa a conexão com PostgreSQL."""

import os
import sys

# Configurar DATABASE_URL
os.environ['DATABASE_URL'] = 'postgresql://cedro_bot_db_user:iSncvowOPA2jhDrulsAwi5tZBtsPpe3O@dpg-d8ee7gurnols73a70o10-a/cedro_bot_db'

from config import _parse_postgres_url

try:
    config = _parse_postgres_url(os.environ['DATABASE_URL'])
    print("[OK] URL parseada com sucesso!")
    print(f"User: {config['user']}")
    print(f"Host: {config['host']}")
    print(f"Port: {config['port']}")
    print(f"Database: {config['database']}")
except Exception as e:
    print(f"[ERRO] Erro: {e}")
    sys.exit(1)
