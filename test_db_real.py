"""Testa a conexão real com Supabase."""

import os

# Configurar variáveis de ambiente do Supabase
os.environ['SUPABASE_USER'] = 'postgres'
os.environ['SUPABASE_PASSWORD'] = '[tiÇ@AMOR123]'
os.environ['SUPABASE_HOST'] = 'db.kqjxaeutnnhhrcjvhadx.supabase.co'
os.environ['SUPABASE_PORT'] = '5432'
os.environ['SUPABASE_DATABASE'] = 'postgres'

import psycopg2
import urllib.parse

# Fazer URL encoding da senha
password = urllib.parse.quote_plus('[tiÇ@AMOR123]')
user = urllib.parse.quote_plus('postgres')
host = 'db.kqjxaeutnnhhrcjvhadx.supabase.co'
port = 5432
database = 'postgres'

dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"

try:
    print("Tentando conectar ao Supabase...")
    conn = psycopg2.connect(dsn)
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
