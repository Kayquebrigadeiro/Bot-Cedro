import html
import logging
from datetime import datetime
from urllib.parse import urlparse

from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import db
from config import ADMIN_IDS, TOKEN


logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


ICON_LEAF = "\U0001f331"
ICON_BOOK = "\U0001f4da"
ICON_FILE = "\U0001f4c4"
ICON_MIC = "\U0001f399\ufe0f"
ICON_PLAY = "\u25b6\ufe0f"
ICON_CAL = "\U0001f4c5"
ICON_CHART = "\U0001f4ca"
ICON_USER = "\U0001f464"
ICON_LINK = "\U0001f517"
ICON_BACK = "\U0001f519"
ICON_ADD = "\u2795"
ICON_TRASH = "\U0001f5d1\ufe0f"
ICON_OK = "\u2705"
ICON_BLOCK = "\u26d4"
ICON_CANCEL = "\u2716\ufe0f"
ICON_GREEN = "\U0001f7e2"
ICON_GEAR = "\u2699\ufe0f"

BRAND = f"{ICON_LEAF} CEDRO"
HEADER = f"<b>{BRAND}</b> | Apoio Psicologico\n" "━━━━━━━━━━━━━━━━━━━━\n"

MAX_TITLE = 80
MAX_DESC = 600
FLOW_KEY = "admin_flow"
FLOW_STAGE_KEY = "admin_flow_stage"
FLOW_DATA_KEY = "admin_flow_data"


def safe(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def fmt_count(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def is_admin(user_id: int | None) -> bool:
    return bool(user_id and user_id in ADMIN_IDS)


def clean_text(value: str | None, limit: int) -> str:
    text = " ".join((value or "").strip().split())
    return text[:limit].strip()


def reset_admin_flow(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    ctx.user_data.pop(FLOW_KEY, None)
    ctx.user_data.pop(FLOW_STAGE_KEY, None)
    ctx.user_data.pop(FLOW_DATA_KEY, None)


def start_admin_flow(ctx: ContextTypes.DEFAULT_TYPE, flow: str) -> None:
    ctx.user_data[FLOW_KEY] = flow
    ctx.user_data[FLOW_STAGE_KEY] = "title"
    ctx.user_data[FLOW_DATA_KEY] = {}


def flow_data(ctx: ContextTypes.DEFAULT_TYPE) -> dict:
    data = ctx.user_data.get(FLOW_DATA_KEY)
    if not isinstance(data, dict):
        data = {}
        ctx.user_data[FLOW_DATA_KEY] = data
    return data


def is_valid_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def home_summary() -> str:
    stats = db.get_stats()
    return (
        "Conteudos organizados para apoio, escuta e acolhimento.\n\n"
        f"{ICON_BOOK} eBooks: <b>{fmt_count(stats['ebooks'])}</b>\n"
        f"{ICON_MIC} Podcasts: <b>{fmt_count(stats['podcasts'])}</b>\n"
        f"{ICON_CAL} Sessoes: <b>{fmt_count(stats['sessions'])}</b>"
    )


def admin_summary() -> str:
    stats = db.get_stats()
    return (
        f"{ICON_USER} Usuarios: <b>{fmt_count(stats['users'])}</b>\n"
        f"{ICON_BOOK} eBooks: <b>{fmt_count(stats['ebooks'])}</b>\n"
        f"{ICON_MIC} Podcasts: <b>{fmt_count(stats['podcasts'])}</b>\n"
        f"{ICON_CAL} Sessoes: <b>{fmt_count(stats['sessions'])}</b>\n"
        f"{ICON_CHART} Acessos: <b>{fmt_count(stats['accesses'])}</b>"
    )


def main_menu_kb(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(f"{ICON_BOOK} eBooks", callback_data="menu_ebooks"),
            InlineKeyboardButton(f"{ICON_MIC} Podcasts", callback_data="menu_podcasts"),
        ],
        [InlineKeyboardButton(f"{ICON_CAL} Sessoes em grupo", callback_data="menu_sessions")],
    ]
    if is_admin(user_id):
        buttons.append([InlineKeyboardButton(f"{ICON_GEAR} Painel admin", callback_data="menu_admin")])
    return InlineKeyboardMarkup(buttons)


def admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(f"{ICON_ADD} Novo eBook", callback_data="admin_add_ebook"),
                InlineKeyboardButton(f"{ICON_ADD} Novo podcast", callback_data="admin_add_podcast"),
            ],
            [InlineKeyboardButton(f"{ICON_ADD} Nova sessao", callback_data="admin_add_session")],
            [
                InlineKeyboardButton(f"{ICON_TRASH} Remover", callback_data="admin_delete"),
                InlineKeyboardButton(f"{ICON_CHART} Estatisticas", callback_data="admin_stats"),
            ],
            [InlineKeyboardButton(f"{ICON_BACK} Menu", callback_data="menu_main")],
        ]
    )


def back_kb(target: str = "menu_main") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(f"{ICON_BACK} Voltar", callback_data=target)]])


def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(f"{ICON_CANCEL} Cancelar", callback_data="cancel_conv")]])


async def send_or_edit(update: Update, text: str, reply_markup: InlineKeyboardMarkup | None = None) -> None:
    if update.callback_query:
        query = update.callback_query
        try:
            await query.edit_message_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )
        except BadRequest as exc:
            if "Message is not modified" not in str(exc):
                raise
        return

    await update.effective_message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )


async def deny_access(update: Update) -> None:
    if update.callback_query:
        await update.callback_query.answer("Acesso restrito a administradores.", show_alert=True)
        return
    if update.effective_message:
        await update.effective_message.reply_text(f"{ICON_BLOCK} Acesso restrito a administradores.")


def admin_only(func):
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id if update.effective_user else None
        if not is_admin(user_id):
            return await deny_access(update)
        return await func(update, ctx)

    wrapper.__name__ = func.__name__
    return wrapper


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    reset_admin_flow(ctx)
    user = update.effective_user
    db.register_user(user.id, user.full_name)
    text = (
        f"{HEADER}"
        f"Ola, <b>{safe(user.first_name)}</b>.\n"
        "Bem-vindo ao ambiente Cedro.\n\n"
        f"{home_summary()}\n\n"
        "Escolha uma area para continuar."
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=main_menu_kb(user.id))


async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        f"{HEADER}"
        "<b>Atalhos</b>\n\n"
        "/start - menu principal\n"
        "/ebooks - listar eBooks\n"
        "/podcasts - listar podcasts\n"
        "/sessoes - listar sessoes\n"
        "/ajuda - ajuda\n"
    )
    if is_admin(update.effective_user.id):
        text += "\n<b>Admin</b>\n/admin - painel administrativo\n/cancelar - cancelar cadastro atual\n"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def button_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    uid = query.from_user.id
    await query.answer()

    try:
        if data == "cancel_conv":
            await cancel(update, ctx)
            return

        if data == "menu_main":
            reset_admin_flow(ctx)
            await send_or_edit(
                update,
                f"{HEADER}<b>Menu principal</b>\n\n{home_summary()}\n\nEscolha uma area.",
                main_menu_kb(uid),
            )
            return

        if data == "menu_ebooks":
            await show_ebooks(query)
            return

        if data == "menu_podcasts":
            await show_podcasts(query)
            return

        if data == "menu_sessions":
            await show_sessions(query)
            return

        if data == "menu_admin":
            if not is_admin(uid):
                await query.answer("Acesso restrito.", show_alert=True)
                return
            reset_admin_flow(ctx)
            await send_or_edit(
                update,
                f"{HEADER}<b>Painel administrativo</b>\n\n{admin_summary()}\n\nEscolha uma acao.",
                admin_menu_kb(),
            )
            return

        if data == "admin_add_ebook":
            await admin_add_ebook_start(update, ctx)
            return

        if data == "admin_add_podcast":
            await admin_add_podcast_start(update, ctx)
            return

        if data == "admin_add_session":
            await admin_add_session_start(update, ctx)
            return

        if data == "admin_stats":
            if not is_admin(uid):
                await query.answer("Acesso restrito.", show_alert=True)
                return
            await send_or_edit(update, f"{HEADER}<b>Estatisticas</b>\n\n{admin_summary()}", back_kb("menu_admin"))
            return

        if data == "admin_delete":
            if not is_admin(uid):
                await query.answer("Acesso restrito.", show_alert=True)
                return
            reset_admin_flow(ctx)
            await send_or_edit(
                update,
                f"{HEADER}<b>Remover item</b>\n\nEscolha o item que deseja remover.",
                all_items_kb(),
            )
            return

        if data.startswith("del_"):
            if not is_admin(uid):
                await query.answer("Acesso restrito.", show_alert=True)
                return
            await delete_item(query, data)
            return

        if data.startswith("ebook_"):
            await send_ebook(query, uid, data)
            return

        if data.startswith("podcast_"):
            await send_podcast(query, uid, data)
            return

        await query.answer("Opcao invalida.", show_alert=True)
    except Exception as exc:
        logger.exception("Erro ao processar callback %s: %s", data, exc)
        await query.message.reply_text("Nao consegui processar essa acao. Tente novamente.")


async def send_ebook(query, uid: int, data: str) -> None:
    try:
        ebook_id = int(data.split("_", 1)[1])
    except (IndexError, ValueError):
        await query.answer("eBook invalido.", show_alert=True)
        return

    ebook = db.get_ebook(ebook_id)
    if not ebook:
        await query.answer("eBook nao encontrado.", show_alert=True)
        return

    db.log_access(uid, "ebook", ebook_id)
    await query.message.reply_document(
        document=ebook["file_id"],
        caption=f"{ICON_BOOK} <b>{safe(ebook['title'])}</b>\n\n{safe(ebook['description'])}",
        parse_mode=ParseMode.HTML,
    )


async def send_podcast(query, uid: int, data: str) -> None:
    try:
        podcast_id = int(data.split("_", 1)[1])
    except (IndexError, ValueError):
        await query.answer("Podcast invalido.", show_alert=True)
        return

    podcast = db.get_podcast(podcast_id)
    if not podcast:
        await query.answer("Podcast nao encontrado.", show_alert=True)
        return

    db.log_access(uid, "podcast", podcast_id)
    await query.message.reply_audio(
        audio=podcast["file_id"],
        caption=f"{ICON_MIC} <b>{safe(podcast['title'])}</b>\n\n{safe(podcast['description'])}",
        parse_mode=ParseMode.HTML,
    )


async def show_ebooks(query) -> None:
    ebooks = db.list_ebooks()
    if not ebooks:
        await query.edit_message_text(
            f"{HEADER}<b>eBooks</b>\n\nNenhum eBook cadastrado ainda.",
            parse_mode=ParseMode.HTML,
            reply_markup=back_kb(),
        )
        return

    buttons = [
        [InlineKeyboardButton(f"{ICON_FILE} {item['title'][:40]}", callback_data=f"ebook_{item['id']}")]
        for item in ebooks
    ]
    buttons.append([InlineKeyboardButton(f"{ICON_BACK} Voltar", callback_data="menu_main")])
    await query.edit_message_text(
        f"{HEADER}<b>eBooks disponiveis</b>\n\n{fmt_count(len(ebooks))} materiais prontos para baixar.",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def show_podcasts(query) -> None:
    podcasts = db.list_podcasts()
    if not podcasts:
        await query.edit_message_text(
            f"{HEADER}<b>Podcasts</b>\n\nNenhum podcast cadastrado ainda.",
            parse_mode=ParseMode.HTML,
            reply_markup=back_kb(),
        )
        return

    buttons = [
        [InlineKeyboardButton(f"{ICON_PLAY} {item['title'][:40]}", callback_data=f"podcast_{item['id']}")]
        for item in podcasts
    ]
    buttons.append([InlineKeyboardButton(f"{ICON_BACK} Voltar", callback_data="menu_main")])
    await query.edit_message_text(
        f"{HEADER}<b>Podcasts</b>\n\n{fmt_count(len(podcasts))} episodios prontos para ouvir.",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def show_sessions(query) -> None:
    sessions = db.list_sessions()
    if not sessions:
        await query.edit_message_text(
            f"{HEADER}<b>Sessoes em grupo</b>\n\nNenhuma sessao agendada ainda.",
            parse_mode=ParseMode.HTML,
            reply_markup=back_kb(),
        )
        return

    text = f"{HEADER}<b>Sessoes em grupo</b>\n\n{fmt_count(len(sessions))} encontros listados.\n\n"
    for item in sessions:
        text += (
            f"{ICON_GREEN} <b>{safe(item['title'])}</b>\n"
            f"{ICON_CAL} {safe(item['date_str'])}\n"
            f"{ICON_LINK} <a href=\"{safe(item['link'])}\">Entrar na sessao</a>\n\n"
        )
    await query.edit_message_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=back_kb(),
        disable_web_page_preview=True,
    )


def all_items_kb() -> InlineKeyboardMarkup:
    buttons = []
    for item in db.list_ebooks():
        buttons.append([InlineKeyboardButton(f"{ICON_BOOK} {item['title'][:40]}", callback_data=f"del_ebook_{item['id']}")])
    for item in db.list_podcasts():
        buttons.append([InlineKeyboardButton(f"{ICON_MIC} {item['title'][:40]}", callback_data=f"del_podcast_{item['id']}")])
    for item in db.list_sessions():
        buttons.append([InlineKeyboardButton(f"{ICON_CAL} {item['title'][:40]}", callback_data=f"del_session_{item['id']}")])
    if not buttons:
        buttons.append([InlineKeyboardButton("Nenhum item cadastrado", callback_data="menu_admin")])
    buttons.append([InlineKeyboardButton(f"{ICON_BACK} Voltar", callback_data="menu_admin")])
    return InlineKeyboardMarkup(buttons)


async def delete_item(query, data: str) -> None:
    parts = data.split("_")
    if len(parts) != 3:
        await query.answer("Acao invalida.", show_alert=True)
        return

    item_type, raw_id = parts[1], parts[2]
    try:
        item_id = int(raw_id)
    except ValueError:
        await query.answer("ID invalido.", show_alert=True)
        return

    handlers = {
        "ebook": (db.delete_ebook, "eBook"),
        "podcast": (db.delete_podcast, "Podcast"),
        "session": (db.delete_session, "Sessao"),
    }
    if item_type not in handlers:
        await query.answer("Tipo invalido.", show_alert=True)
        return

    delete_func, label = handlers[item_type]
    delete_func(item_id)
    await query.edit_message_text(f"{ICON_OK} {label} removido com sucesso.", reply_markup=back_kb("menu_admin"))


@admin_only
async def admin_add_ebook_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    reset_admin_flow(ctx)
    start_admin_flow(ctx, "ebook")
    await send_or_edit(update, f"{HEADER}<b>Novo eBook</b>\n\nEtapa 1 de 3: envie o titulo.", cancel_kb())


@admin_only
async def admin_add_podcast_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    reset_admin_flow(ctx)
    start_admin_flow(ctx, "podcast")
    await send_or_edit(update, f"{HEADER}<b>Novo podcast</b>\n\nEtapa 1 de 3: envie o titulo.", cancel_kb())


@admin_only
async def admin_add_session_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    reset_admin_flow(ctx)
    start_admin_flow(ctx, "session")
    await send_or_edit(update, f"{HEADER}<b>Nova sessao</b>\n\nEtapa 1 de 3: envie o titulo.", cancel_kb())


async def handle_admin_flow(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> bool:
    flow = ctx.user_data.get(FLOW_KEY)
    stage = ctx.user_data.get(FLOW_STAGE_KEY)
    message = update.effective_message

    logger.info(f"handle_admin_flow - flow={flow}, stage={stage}, message={message is not None}")

    if not flow or not stage or message is None:
        return False

    if not is_admin(update.effective_user.id if update.effective_user else None):
        reset_admin_flow(ctx)
        await message.reply_text(f"{ICON_BLOCK} Cadastro cancelado: acesso restrito.")
        return True

    data = flow_data(ctx)
    logger.info(f"handle_admin_flow - data={data}")

    if flow == "ebook":
        return await handle_ebook_flow(message, ctx, stage, data)
    if flow == "podcast":
        return await handle_podcast_flow(message, ctx, stage, data)
    if flow == "session":
        return await handle_session_flow(message, ctx, stage, data)

    reset_admin_flow(ctx)
    return False


async def handle_ebook_flow(message, ctx: ContextTypes.DEFAULT_TYPE, stage: str, data: dict) -> bool:
    logger.info(f"handle_ebook_flow - stage={stage}")
    
    if stage == "title":
        if not message.text:
            await message.reply_text("Envie uma mensagem de texto com o titulo.")
            return True
        title = clean_text(message.text, MAX_TITLE)
        if len(title) < 3:
            await message.reply_text("Envie um titulo com pelo menos 3 caracteres.")
            return True
        data["title"] = title
        ctx.user_data[FLOW_STAGE_KEY] = "desc"
        logger.info(f"handle_ebook_flow - title={title}, stage now=desc")
        await message.reply_text("Etapa 2 de 3: envie uma descricao curta.", reply_markup=cancel_kb())
        return True

    if stage == "desc":
        if not message.text:
            await message.reply_text("Envie uma mensagem de texto com a descricao.")
            return True
        desc = clean_text(message.text, MAX_DESC)
        if len(desc) < 5:
            await message.reply_text("Envie uma descricao com pelo menos 5 caracteres.")
            return True
        data["desc"] = desc
        ctx.user_data[FLOW_STAGE_KEY] = "file"
        logger.info(f"handle_ebook_flow - desc={desc}, stage now=file")
        await message.reply_text("Etapa 3 de 3: envie o PDF do eBook.", reply_markup=cancel_kb())
        return True

    if stage == "file":
        if not message.document:
            await message.reply_text("Envie um arquivo PDF.")
            return True
        filename = (message.document.file_name or "").lower()
        mime = message.document.mime_type or ""
        if mime != "application/pdf" and not filename.endswith(".pdf"):
            await message.reply_text("Arquivo invalido. Envie um PDF.")
            return True
        db.add_ebook(data["title"], data["desc"], message.document.file_id)
        logger.info(f"handle_ebook_flow - saved ebook {data['title']}")
        await message.reply_text(
            f"{ICON_OK} eBook <b>{safe(data['title'])}</b> salvo com sucesso.",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_menu_kb(),
        )
        reset_admin_flow(ctx)
        return True

    logger.warning(f"handle_ebook_flow - unknown stage {stage}")
    return False


async def handle_podcast_flow(message, ctx: ContextTypes.DEFAULT_TYPE, stage: str, data: dict) -> bool:
    if stage == "title":
        if not message.text:
            await message.reply_text("Envie uma mensagem de texto com o titulo.")
            return True
        title = clean_text(message.text, MAX_TITLE)
        if len(title) < 3:
            await message.reply_text("Envie um titulo com pelo menos 3 caracteres.")
            return True
        data["title"] = title
        ctx.user_data[FLOW_STAGE_KEY] = "desc"
        await message.reply_text("Etapa 2 de 3: envie uma descricao curta.", reply_markup=cancel_kb())
        return True

    if stage == "desc":
        if not message.text:
            await message.reply_text("Envie uma mensagem de texto com a descricao.")
            return True
        desc = clean_text(message.text, MAX_DESC)
        if len(desc) < 5:
            await message.reply_text("Envie uma descricao com pelo menos 5 caracteres.")
            return True
        data["desc"] = desc
        ctx.user_data[FLOW_STAGE_KEY] = "file"
        await message.reply_text("Etapa 3 de 3: envie um audio, voz ou arquivo de audio.", reply_markup=cancel_kb())
        return True

    if stage == "file":
        file_id = None
        
        if message.audio:
            file_id = message.audio.file_id
        elif message.voice:
            file_id = message.voice.file_id
        elif message.document:
            filename = (message.document.file_name or "").lower()
            mime = message.document.mime_type or ""
            if mime.startswith("audio/") or filename.endswith((".mp3", ".ogg", ".m4a", ".wav", ".aac", ".flac")):
                file_id = message.document.file_id
        
        if not file_id:
            await message.reply_text("Envie um audio, voz ou arquivo de audio (MP3, OGG, M4A, WAV, AAC, FLAC).")
            return True
        
        db.add_podcast(data["title"], data["desc"], file_id)
        await message.reply_text(
            f"{ICON_OK} Podcast <b>{safe(data['title'])}</b> salvo com sucesso.",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_menu_kb(),
        )
        reset_admin_flow(ctx)
        return True

    return False


async def handle_session_flow(message, ctx: ContextTypes.DEFAULT_TYPE, stage: str, data: dict) -> bool:
    if stage == "title":
        if not message.text:
            await message.reply_text("Envie uma mensagem de texto com o titulo.")
            return True
        title = clean_text(message.text, MAX_TITLE)
        if len(title) < 3:
            await message.reply_text("Envie um titulo com pelo menos 3 caracteres.")
            return True
        data["title"] = title
        ctx.user_data[FLOW_STAGE_KEY] = "date"
        await message.reply_text(
            "Etapa 2 de 3: envie data e horario no formato DD/MM/AAAA HH:MM.\nExemplo: 02/06/2026 19:00",
            reply_markup=cancel_kb(),
        )
        return True

    if stage == "date":
        if not message.text:
            await message.reply_text("Envie uma mensagem de texto com a data.")
            return True
        raw = message.text.strip()
        try:
            date_value = datetime.strptime(raw, "%d/%m/%Y %H:%M")
        except ValueError:
            await message.reply_text("Formato invalido. Use DD/MM/AAAA HH:MM.")
            return True
        if date_value < datetime.now():
            await message.reply_text("A sessao precisa estar em uma data futura.")
            return True
        data["date_str"] = date_value.strftime("%d/%m/%Y as %H:%M")
        data["date_ts"] = int(date_value.timestamp())
        ctx.user_data[FLOW_STAGE_KEY] = "link"
        await message.reply_text("Etapa 3 de 3: envie o link da chamada.", reply_markup=cancel_kb())
        return True

    if stage == "link":
        if not message.text:
            await message.reply_text("Envie uma mensagem de texto com o link.")
            return True
        link = message.text.strip()
        if not is_valid_url(link):
            await message.reply_text("Envie um link valido com http:// ou https://.")
            return True

        db.add_session(data["title"], data["date_str"], link, data["date_ts"])
        await message.reply_text(
            f"{ICON_OK} Sessao <b>{safe(data['title'])}</b> salva para {safe(data['date_str'])}.",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_menu_kb(),
        )
        await notify_users_about_session(ctx, data["title"], data["date_str"], link)
        reset_admin_flow(ctx)
        return True

    return False


async def notify_users_about_session(ctx: ContextTypes.DEFAULT_TYPE, title: str, date_str: str, link: str) -> None:
    users = db.list_users()
    text = (
        f"{HEADER}<b>Nova sessao em grupo</b>\n\n"
        f"{ICON_CAL} <b>{safe(title)}</b>\n"
        f"{ICON_CAL} {safe(date_str)}\n"
        f"{ICON_LINK} <a href=\"{safe(link)}\">Entrar na sessao</a>"
    )
    sent = 0
    for user_id in users:
        try:
            await ctx.bot.send_message(user_id, text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            sent += 1
        except Exception as exc:
            logger.info("Nao foi possivel notificar usuario %s: %s", user_id, exc)
    logger.info("Sessao '%s' notificada para %s/%s usuarios.", title, sent, len(users))


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    reset_admin_flow(ctx)
    if update.callback_query:
        await send_or_edit(update, "Operacao cancelada.", back_kb("menu_admin"))
        return
    await update.message.reply_text("Operacao cancelada.", reply_markup=admin_menu_kb())


async def cmd_ebooks(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await show_ebooks(MessageReplyAdapter(update.message))


async def cmd_podcasts(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await show_podcasts(MessageReplyAdapter(update.message))


async def cmd_sessions(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await show_sessions(MessageReplyAdapter(update.message))


class MessageReplyAdapter:
    def __init__(self, message):
        self.message = message

    async def edit_message_text(self, text, **kwargs):
        await self.message.reply_text(text, **kwargs)


async def cmd_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(f"{ICON_BLOCK} Acesso negado.")
        return
    reset_admin_flow(ctx)
    await update.message.reply_text(
        f"{HEADER}<b>Painel administrativo</b>\n\n{admin_summary()}\n\nEscolha uma acao.",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_menu_kb(),
    )


async def message_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if await handle_admin_flow(update, ctx):
        return
    await update.message.reply_text("Use /start para abrir o menu principal.", reply_markup=main_menu_kb(update.effective_user.id))


async def error_handler(update: object, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Erro nao capturado: %s", ctx.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text("Ocorreu um erro. Use /start e tente novamente.")
        except Exception:
            logger.exception("Falha ao enviar mensagem de erro ao usuario.")


async def setup_commands(app: Application) -> None:
    await app.bot.set_my_commands(
        [
            BotCommand("start", "Abrir menu principal"),
            BotCommand("ebooks", "Ver eBooks"),
            BotCommand("podcasts", "Ver podcasts"),
            BotCommand("sessoes", "Ver sessoes"),
            BotCommand("ajuda", "Ajuda"),
            BotCommand("admin", "Painel admin"),
            BotCommand("cancelar", "Cancelar cadastro"),
        ]
    )


def build_app() -> Application:
    if not TOKEN:
        raise RuntimeError("Defina BOT_TOKEN no arquivo .env ou nas variaveis de ambiente.")

    app = Application.builder().token(TOKEN).post_init(setup_commands).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ajuda", help_cmd))
    app.add_handler(CommandHandler("ebooks", cmd_ebooks))
    app.add_handler(CommandHandler("podcasts", cmd_podcasts))
    app.add_handler(CommandHandler("sessoes", cmd_sessions))
    app.add_handler(CommandHandler("admin", cmd_admin))
    app.add_handler(CommandHandler("cancelar", cancel))
    app.add_handler(CommandHandler("addebook", admin_add_ebook_start))
    app.add_handler(CommandHandler("addpodcast", admin_add_podcast_start))
    app.add_handler(CommandHandler("addsessao", admin_add_session_start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))
    app.add_handler(MessageHandler(filters.Document.ALL & ~filters.COMMAND, message_router))
    app.add_error_handler(error_handler)
    return app


async def main() -> None:
    db.init()
    app = build_app()
    logger.info("%s iniciado.", BRAND)
    
    # Servidor web fake para Render
    from aiohttp import web
    async def health(request):
        return web.Response(text="Bot online")
    
    web_app = web.Application()
    web_app.router.add_get("/", health)
    runner = web.AppRunner(web_app)
    await runner.setup()
    
    import os
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info("Servidor web na porta %s", port)
    
    # Inicia bot
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)
    import asyncio
    await asyncio.Event().wait()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
