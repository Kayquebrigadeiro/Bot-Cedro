# Instruções para configurar Supabase

## PASSO 1: Criar conta no Supabase

1. Acesse https://supabase.com
2. Clique em "Start your project" ou "Sign Up"
3. Crie uma conta (pode usar GitHub/Google/Email)

## PASSO 2: Criar novo projeto

1. Clique em "New Project"
2. Preencha:
   - **Name**: `cedro-bot`
   - **Database Password**: (escolha uma senha forte)
   - **Region**: Escolha **South America (São Paulo)** ou **US East**
   - **Pricing Plan**: Free (gratuito)
3. Clique em "Create new project"
4. **Aguarde** 2-3 minutos até o projeto estar pronto

## PASSO 3: Copiar a DATABASE_URL

1. No seu projeto, clique em **"Settings"** > **"Database"**
2. Copie a **Connection string** (estilo PostgreSQL)
3. Deve ter o formato: `postgresql://user:password@host:port/database`

Exemplo:
```
postgresql://postgres:SENHA_AQUI@db.xxxxxxxxxxxxxx.supabase.co:5432/postgres
```

## PASSO 4: Configurar no Render

1. No seu Web Service do bot, clique em **"Environment"**
2. Clique em **"Add Environment Variable"**
3. Preencha:
   - **Name**: `DATABASE_URL`
   - **Value**: (cole a URL do Supabase)
4. Clique em **"Save"**

## PASSO 5: Redeploy

1. O Render fará deploy automaticamente
2. Ou clique em **"Manual Deploy"** > **"Deploy latest commit"**
3. Aguarde 5-10 minutos

## PASSO 6: Verificar

1. No console do Render, veja os logs
2. O bot deve criar as tabelas automaticamente
3. Tente cadastrar um eBook ou podcast
4. Reinicie o Web Service
5. Verifique se os dados persistiram

## Vantagens do Supabase:
- Interface amigável e fácil de usar
- Plano gratuito generoso (500 MB de armazenamento)
- Backup automático
- Dashboard para visualizar dados
- Não precisa configurar firewall ou IPs