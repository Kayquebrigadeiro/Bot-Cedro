# Instruções para configurar PostgreSQL no Render

## PASSO 1: Copiar a DATABASE_URL CORRETA

1. Acesse https://render.com
2. Clique no seu banco de dados (`cedro-bot-db`)
3. Vá na aba **"Connection string"**
4. Copie a **string completa** que aparece (deve ter o formato completo)

A URL completa deve ter este formato:
```
postgresql://user:password@host:port/database
```

Exemplo de URL completa:
```
postgresql://cedro_bot_db_user:iSncvowOPA2jhDrulsAwi5tZBtsPpe3O@dpg-d8ee7gurnols73a70o10-a.svc.railway.internal:5432/cedro_bot_db
```

## PASSO 2: Configurar no Web Service

1. No seu Web Service do bot, clique em **"Environment"**
2. Clique em **"Add Environment Variable"**
3. Preencha:
   - **Name**: `DATABASE_URL`
   - **Value**: (cole a URL completa que você copiou)
4. Clique em **"Save"**

## PASSO 3: Remover DB_FILE (opcional)

Se quiser usar apenas PostgreSQL:
1. Encontre a variável `DB_FILE`
2. Clique no ícone de lixo para removê-la
3. Clique em **"Save"**

## PASSO 4: Redeploy

1. O Render fará deploy automaticamente
2. Ou clique em **"Manual Deploy"** > **"Deploy latest commit"**
3. Aguarde 5-10 minutos

## PASSO 5: Verificar

1. No console do Render, veja os logs
2. O bot deve criar as tabelas automaticamente
3. Tente cadastrar um eBook ou podcast
4. Reinicie o Web Service
5. Verifique se os dados persistiram

## DÚVIDAS?

Se a URL estiver incompleta, copie novamente da aba "Connection string" do banco de dados.