# config.py — Configurações do Bot CEDRO
# ──────────────────────────────────────────────────────────────────────────────
# PASSO 1: Crie seu bot com o @BotFather no Telegram e cole o token abaixo.
# PASSO 2: Adicione os IDs dos administradores na lista ADMIN_IDS.
#          Para saber seu ID, envie /start para o bot @userinfobot no Telegram.
# ──────────────────────────────────────────────────────────────────────────────

# Token do bot (obtido via @BotFather)
TOKEN = "SEU_TOKEN_AQUI"

# IDs dos administradores (int)
# Exemplo: ADMIN_IDS = {123456789, 987654321}
ADMIN_IDS = {
    123456789,   # ← substitua pelo seu ID real
}

# Caminho do banco de dados SQLite
DB_FILE = "cedro.db"
