# Deploy no Render com Supabase - PASSO A PASSO COMPLETO

## PASSO 1: Criar as tabelas no Supabase

1. Acesse https://supabase.com e faça login
2. Vá no seu projeto (`cedro-bot`)
3. Clique em **"SQL Editor"** no menu lateral
4. Clique em **"New query"**
5. Copie todo o conteúdo do arquivo `supabase_schema.sql`
6. Cole no editor SQL
7. Clique em **"Run"** (ou pressione Ctrl+Enter)
8. Aguarde a mensagem de sucesso

## PASSO 2: Copiar a Connection String do Supabase

1. No Supabase, clique em **"Settings"** > **"Database"**
2. Role até **"Connection string"**
3. Copie a **Connection string** (formato: `postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres`)
4. **IMPORTANTE**: Substitua `[PASSWORD]` pela senha que você criou no projeto

Exemplo:
```
postgresql://postgres:SUA_SENHA_AQUI@db.kqjxaeutnnhhrcjvhadx.supabase.co:5432/postgres
```

## PASSO 3: Fazer commit e push do código

1. Abra o terminal no diretório do projeto
2. Execute:
```bash
git add .
git commit -m "Atualizando para usar Supabase"
git push origin main
```

## PASSO 4: Criar Web Service no Render

1. Acesse https://render.com e faça login
2. Clique em **"New +"** > **"Web Service"**
3. Conecte seu repositório GitHub: `Kayquebrigadeiro/Bot-Cedro`
4. Configure:
   - **Name**: `cedro-bot`
   - **Region**: US East (N. Virginia)
   - **Branch**: `main`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`

## PASSO 5: Adicionar variáveis de ambiente no Render

No painel "Environment", adicione:

| Name | Value |
|------|-------|
| `BOT_TOKEN` | `8673350027:AAGivpbzWPbjqxZ1ItjkUcCWmVpXGwNN1C8` |
| `ADMIN_IDS` | `6197047295` |
| `DATABASE_URL` | (cole a Connection string do Supabase) |

**IMPORTANTE**: A `DATABASE_URL` deve ter o formato:
```
postgresql://postgres:SUA_SENHA@db.kqjxaeutnnhhrcjvhadx.supabase.co:5432/postgres
```

## PASSO 6: Deploy

1. Clique em **"Create Web Service"**
2. Aguarde 5-10 minutos até o deploy completar
3. Verifique os logs para garantir que não houve erros

## PASSO 7: Testar

1. Abra seu bot no Telegram
2. Envie `/start`
3. Tente cadastrar um eBook ou podcast
4. Verifique no Supabase se os dados foram salvos:
   - Vá em **"Table Editor"**
   - Selecione a tabela `ebooks` ou `podcasts`
   - Veja se os dados aparecem

## PASSO 8: Verificar persistência

1. No Render, clique em **"Manual Deploy"** > **"Deploy latest commit"**
2. Aguarde o redeploy
3. Abra o bot novamente
4. Verifique se os eBooks/podcasts ainda estão lá

---

## Vantagens desta solução:

✅ Dados persistem mesmo se o Render reiniciar
✅ Fácil de visualizar dados no Supabase
✅ Backup automático
✅ Gratuito (até 500 MB)
✅ Não precisa configurar firewall ou IPs

## Troubleshooting:

**Erro de conexão?**
- Verifique se a `DATABASE_URL` está correta
- Verifique se a senha não tem caracteres especiais problemáticos
- Tente usar a senha sem caracteres especiais

**Tabelas não foram criadas?**
- Execute o script SQL novamente no Supabase
- Verifique se não há erros no SQL Editor

**Bot não inicia?**
- Verifique os logs no Render
- Verifique se todas as variáveis de ambiente estão configuradas
