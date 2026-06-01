# CEDRO Bot

Bot de apoio psicológico no Telegram para organizar e distribuir eBooks, podcasts e sessões em grupo.

## Funcionalidades

- Menu principal com botões para eBooks, podcasts e sessões.
- Painel administrativo protegido por ID do Telegram.
- Cadastro de eBooks em PDF com validação de arquivo.
- Cadastro de podcasts por áudio, voz ou arquivo de áudio.
- Agendamento de sessões futuras com validação de data e link.
- Notificação automática dos usuários cadastrados quando uma sessão é criada.
- Estatísticas de usuários, conteúdos, sessões e acessos.
- Banco SQLite local, leve e pronto para deploy.

## Configuração

Crie variáveis de ambiente ou um arquivo `.env` local:

```env
BOT_TOKEN=token_do_botfather
ADMIN_IDS=6197047295
DB_FILE=cedro.db
```

Para descobrir seu ID, envie uma mensagem para `@userinfobot` no Telegram.

## Rodar localmente

```bash
pip install -r requirements.txt
$env:BOT_TOKEN="token_do_botfather"
$env:ADMIN_IDS="6197047295"
python bot.py
```

No Linux:

```bash
export BOT_TOKEN="token_do_botfather"
export ADMIN_IDS="6197047295"
python bot.py
```

## Deploy no Discloud

Arquivos necessários já estão no projeto:

- `discloud.config`
- `requirements.txt`
- `bot.py`
- `db.py`
- `config.py`

Configure no Discloud as variáveis `BOT_TOKEN` e `ADMIN_IDS`. Depois envie o projeto compactado ou use o método de upload que você já utiliza na plataforma.

## Comandos

| Comando | Descrição |
| --- | --- |
| `/start` | Abre o menu principal |
| `/ebooks` | Lista eBooks disponíveis |
| `/podcasts` | Lista podcasts disponíveis |
| `/sessoes` | Lista sessões agendadas |
| `/ajuda` | Mostra ajuda |
| `/admin` | Abre o painel administrativo |
| `/cancelar` | Cancela uma operação em andamento |

## Observação de segurança

O token do bot não fica mais fixo no código. Para apresentação e deploy, deixe `BOT_TOKEN` configurado no ambiente.
