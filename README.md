# 🌿 CEDRO BOT — Apoio Psicológico no Telegram

Bot do projeto **Cedro** para organização de conteúdos de apoio psicológico: eBooks, podcasts e sessões em grupo.

---

## ⚙️ Configuração Inicial

### 1. Criar o bot no Telegram
1. Abra o Telegram e busque por **@BotFather**
2. Envie `/newbot` e siga as instruções
3. Copie o **token** gerado

### 2. Descobrir seu ID de administrador
1. Busque por **@userinfobot** no Telegram
2. Envie qualquer mensagem — ele retorna seu ID numérico

### 3. Editar o `config.py`
```python
TOKEN = "SEU_TOKEN_AQUI"      # Token do BotFather
ADMIN_IDS = {SEU_ID_AQUI}     # Seu ID numérico
```

---

## 🚀 Instalação e Execução

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar o bot
python bot.py
```

---

## 📋 Comandos

### Usuários
| Comando | Descrição |
|---------|-----------|
| `/start` | Menu principal |
| `/ebooks` | Lista de eBooks disponíveis |
| `/podcasts` | Lista de podcasts |
| `/sessoes` | Sessões em grupo agendadas |
| `/ajuda` | Ajuda e lista de comandos |

### Administradores
| Comando | Descrição |
|---------|-----------|
| `/admin` | Painel administrativo |
| `/addebook` | Adicionar novo eBook |
| `/addpodcast` | Adicionar novo podcast |
| `/addsessao` | Agendar sessão em grupo |
| `/cancelar` | Cancelar operação em andamento |

---

## 🗂️ Estrutura de Arquivos

```
cedro_bot/
├── bot.py          # Lógica principal do bot
├── db.py           # Banco de dados SQLite
├── config.py       # Token e configurações
├── requirements.txt
└── README.md
```

---

## ✨ Funcionalidades

- **eBooks**: Upload de PDFs diretamente no Telegram. Usuários baixam com um clique.
- **Podcasts**: Upload de áudios (MP3/OGG). Usuários ouvem diretamente no app.
- **Sessões em Grupo**: Agendamento com data/hora e link de chamada. Todos os usuários recebem notificação automática.
- **Painel Admin**: Interface de botões para gerenciar todo o conteúdo.
- **Estatísticas**: Visualização de usuários, eBooks, podcasts e sessões cadastradas.
- **Logs de acesso**: Rastreamento de quais conteúdos foram acessados.

---

## 💡 Por que Telegram?

- Suporte nativo a envio/recebimento de arquivos (PDF, áudio) via API
- Notificações push confiáveis e gratuitas
- Interface de botões rica e interativa
- Grupos e canais ilimitados
- API robusta e bem documentada
- Sem custo adicional de servidores para armazenar arquivos (o Telegram armazena)
