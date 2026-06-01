# Instruções para deploy no Render com persistência de dados

## Passo 1: Criar Web Service
1. Acesse https://render.com
2. Clique em "New +" > "Web Service"
3. Conecte seu repositório GitHub

## Passo 2: Configurar Variáveis de Ambiente
No painel "Environment", adicione:
- `BOT_TOKEN` = seu token do BotFather
- `ADMIN_IDS` = seus IDs de administrador (separados por vírgula)
- `DB_FILE` = cedro.db

## Passo 3: Configurar Armazenamento Persistente (IMPORTANTE!)
1. No seu Web Service, clique em "Storage"
2. Clique em "Add Disk"
3. **Path**: `/opt/render/project/src`
4. **Size**: 1 GB (gratuito)
5. Clique em "Save"

## Passo 4: Deploy
1. Clique em "Create Web Service"
2. Aguarde o deploy (5-10 minutos)
3. O bot estará disponível na URL gerada

## Como funciona a persistência:
- O arquivo `cedro.db` será salvo no armazenamento persistente
- Quando o serviço reiniciar, os eBooks, podcasts e sessões continuarão lá
- O banco de dados SQLite é leve e perfeito para bots pequenos

## Backup recomendado:
- A cada 7 dias, faça backup do arquivo `cedro.db`
- Você pode baixar o backup através do painel "Storage" do Render
