# Deploy no Render com Supabase - SIMPLES E DIRETO

## PASSO 1: Criar as tabelas no Supabase

1. Acesse https://supabase.com
2. Vá no seu projeto
3. Clique em **"SQL Editor"**
4. Copie o conteúdo do arquivo `supabase_schema.sql`
5. Cole e clique em **"Run"**

## PASSO 2: Fazer deploy no Render

1. Acesse https://render.com
2. Clique em **"New +"** > **"Web Service"**
3. Conecte o repositório: `Kayquebrigadeiro/Bot-Cedro`
4. Configure:
   - **Name**: `cedro-bot`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`

## PASSO 3: Adicionar variáveis de ambiente

No Render, adicione estas variáveis:

```
BOT_TOKEN=8673350027:AAGivpbzWPbjqxZ1ItjkUcCWmVpXGwNN1C8
ADMIN_IDS=6197047295
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@db.kqjxaeutnnhhrcjvhadx.supabase.co:5432/postgres
```

**IMPORTANTE**: Substitua `[YOUR_PASSWORD]` pela senha do seu projeto Supabase.

## PASSO 4: Deploy

Clique em **"Create Web Service"** e pronto!

---

## Pronto!

Seu bot vai:
- ✅ Conectar no Supabase
- ✅ Salvar eBooks e podcasts
- ✅ Dados persistem mesmo se reiniciar
