"""Testa a conexão real com PostgreSQL."""

import os

# Configurar DATABASE_URL - formato correto do Render
os.environ['DATABASE_URL'] = 'postgresql://cedro_bot_db_user:iSncvowOPA2jhDrulsAwi5tZBtsPpe3O@dpg-d8ee7gurnols73a70o10-a.cedro-bot-db.svc.railway.internal:5432/cedro_bot_db'

import psycopg2

try:
    print("Tentando conectar ao PostgreSQL...")
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    print("[OK] Conectado com sucesso!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"PostgreSQL version: {version[0]}")
    
    cursor.close()
    conn.close()
    print("\n[OK] Teste de conexão finalizado!")
    
except Exception as e:
    print(f"[ERRO] Erro na conexão: {e}")
    import traceback
    traceback.print_exc()
