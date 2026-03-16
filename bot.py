import logging
import json
import os
from datetime import datetime
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    BotCommand
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from telegram.constants import ParseMode
from config import TOKEN, ADMIN_IDS, DB_FILE
import db

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── Estados do ConversationHandler ────────────────────────────────────────────
(
    ADD_EBOOK_TITLE, ADD_EBOOK_DESC, ADD_EBOOK_FILE,
    ADD_PODCAST_TITLE, ADD_PODCAST_DESC, ADD_PODCAST_FILE,
    ADD_SESSION_TITLE, ADD_SESSION_DATE, ADD_SESSION_LINK,
    EDIT_CHOOSE, EDIT_VALUE,
    DELETE_CHOOSE,
) = range(12)

# HELPERS

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def admin_only(func):
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if not is_admin(uid):
            await update.message.reply_text("⛔ Acesso restrito a administradores.")
            return ConversationHandler.END
        return await func(update, ctx)
    wrapper.__name__ = func.__name__
    return wrapper

def main_menu_kb(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("📚 eBooks", callback_data="menu_ebooks"),
         InlineKeyboardButton("🎙️ Podcasts", callback_data="menu_podcasts")],
        [InlineKeyboardButton("📅 Sessões em Grupo", callback_data="menu_sessions")],
    ]
    if is_admin(user_id):
        buttons.append([InlineKeyboardButton("⚙️ Painel Admin", callback_data="menu_admin")])
    return InlineKeyboardMarkup(buttons)

def admin_menu_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("➕ Adicionar eBook", callback_data="admin_add_ebook"),
         InlineKeyboardButton("➕ Adicionar Podcast", callback_data="admin_add_podcast")],
        [InlineKeyboardButton("➕ Agendar Sessão", callback_data="admin_add_session")],
        [InlineKeyboardButton("🗑️ Remover Item", callback_data="admin_delete"),
         InlineKeyboardButton("📊 Estatísticas", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(buttons)

def back_kb(target="menu_main") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Voltar", callback_data=target)]])

def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancelar", callback_data="cancel_conv")]])

CEDRO_HEADER = (
    "🌿 *CEDRO* — Apoio Psicológico\n"
    "━━━━━━━━━━━━━━━━━━━━━━━\n"
)

# COMANDOS GERAIS

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    db.register_user(update.effective_user.id, update.effective_user.full_name)
    text = (
        f"{CEDRO_HEADER}"
        f"Olá, *{update.effective_user.first_name}*! 👋\n\n"
        "Bem-vindo ao espaço de apoio psicológico do Cedro.\n"
        "Aqui você encontra recursos para cuidar da sua saúde mental.\n\n"
        "O que deseja acessar?"
    )
    await update.message.reply_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu_kb(update.effective_user.id)
    )

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        f"{CEDRO_HEADER}"
        "📖 *Comandos disponíveis:*\n\n"
        "/start — Menu principal\n"
        "/ebooks — Ver eBooks disponíveis\n"
        "/podcasts — Ver podcasts\n"
        "/sessoes — Ver sessões agendadas\n"
        "/ajuda — Esta mensagem\n"
    )
    if is_admin(update.effective_user.id):
        text += (
            "\n🔧 *Comandos Admin:*\n"
            "/admin — Painel administrativo\n"
        )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# MENUS INLINE

async def button_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = query.from_user.id

    if data == "menu_main":
        await query.edit_message_text(
            f"{CEDRO_HEADER}O que deseja acessar?",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_menu_kb(uid)
        )

    elif data == "menu_ebooks":
        await show_ebooks(query)

    elif data == "menu_podcasts":
        await show_podcasts(query)

    elif data == "menu_sessions":
        await show_sessions(query)

    elif data == "menu_admin" and is_admin(uid):
        await query.edit_message_text(
            f"{CEDRO_HEADER}⚙️ *Painel Administrativo*\n\nEscolha uma ação:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=admin_menu_kb()
        )

    elif data == "admin_stats" and is_admin(uid):
        stats = db.get_stats()
        text = (
            f"{CEDRO_HEADER}📊 *Estatísticas*\n\n"
            f"👤 Usuários: {stats['users']}\n"
            f"📚 eBooks: {stats['ebooks']}\n"
            f"🎙️ Podcasts: {stats['podcasts']}\n"
            f"📅 Sessões agendadas: {stats['sessions']}\n"
        )
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_kb("menu_admin"))

    elif data.startswith("ebook_"):
        eid = int(data.split("_")[1])
        ebook = db.get_ebook(eid)
        if ebook:
            db.log_access(uid, "ebook", eid)
            await query.message.reply_document(
                document=ebook["file_id"],
                caption=f"📚 *{ebook['title']}*\n\n{ebook['description']}",
                parse_mode=ParseMode.MARKDOWN
            )

    elif data.startswith("podcast_"):
        pid = int(data.split("_")[1])
        podcast = db.get_podcast(pid)
        if podcast:
            db.log_access(uid, "podcast", pid)
            await query.message.reply_audio(
                audio=podcast["file_id"],
                caption=f"🎙️ *{podcast['title']}*\n\n{podcast['description']}",
                parse_mode=ParseMode.MARKDOWN
            )

    elif data == "admin_delete" and is_admin(uid):
        ctx.user_data["step"] = "delete_choose"
        items = _all_items_kb()
        await query.edit_message_text(
            f"{CEDRO_HEADER}🗑️ *Remover Item*\n\nEscolha o item para remover:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=items
        )

    elif data.startswith("del_ebook_") and is_admin(uid):
        eid = int(data.split("_")[2])
        db.delete_ebook(eid)
        await query.edit_message_text("✅ eBook removido com sucesso!", reply_markup=back_kb("menu_admin"))

    elif data.startswith("del_podcast_") and is_admin(uid):
        pid = int(data.split("_")[2])
        db.delete_podcast(pid)
        await query.edit_message_text("✅ Podcast removido com sucesso!", reply_markup=back_kb("menu_admin"))

    elif data.startswith("del_session_") and is_admin(uid):
        sid = int(data.split("_")[2])
        db.delete_session(sid)
        await query.edit_message_text("✅ Sessão removida com sucesso!", reply_markup=back_kb("menu_admin"))


# EXIBIÇÃO DE CONTEÚDO

async def show_ebooks(query):
    ebooks = db.list_ebooks()
    if not ebooks:
        await query.edit_message_text(
            f"{CEDRO_HEADER}📚 *eBooks*\n\nNenhum eBook disponível no momento.",
            parse_mode=ParseMode.MARKDOWN, reply_markup=back_kb()
        )
        return
    buttons = [[InlineKeyboardButton(f"📄 {e['title']}", callback_data=f"ebook_{e['id']}")] for e in ebooks]
    buttons.append([InlineKeyboardButton("🔙 Voltar", callback_data="menu_main")])
    await query.edit_message_text(
        f"{CEDRO_HEADER}📚 *eBooks Disponíveis*\n\nEscolha um eBook para baixar:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_podcasts(query):
    podcasts = db.list_podcasts()
    if not podcasts:
        await query.edit_message_text(
            f"{CEDRO_HEADER}🎙️ *Podcasts*\n\nNenhum podcast disponível no momento.",
            parse_mode=ParseMode.MARKDOWN, reply_markup=back_kb()
        )
        return
    buttons = [[InlineKeyboardButton(f"▶️ {p['title']}", callback_data=f"podcast_{p['id']}")] for p in podcasts]
    buttons.append([InlineKeyboardButton("🔙 Voltar", callback_data="menu_main")])
    await query.edit_message_text(
        f"{CEDRO_HEADER}🎙️ *Podcasts*\n\nEscolha um episódio para ouvir:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_sessions(query):
    sessions = db.list_sessions()
    if not sessions:
        await query.edit_message_text(
            f"{CEDRO_HEADER}📅 *Sessões em Grupo*\n\nNenhuma sessão agendada no momento.",
            parse_mode=ParseMode.MARKDOWN, reply_markup=back_kb()
        )
        return
    text = f"{CEDRO_HEADER}📅 *Sessões em Grupo Agendadas*\n\n"
    for s in sessions:
        text += (
            f"🟢 *{s['title']}*\n"
            f"   🗓️ {s['date_str']}\n"
            f"   🔗 [Entrar na sessão]({s['link']})\n\n"
        )
    await query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=back_kb(), disable_web_page_preview=True
    )

def _all_items_kb() -> InlineKeyboardMarkup:
    buttons = []
    for e in db.list_ebooks():
        buttons.append([InlineKeyboardButton(f"📚 {e['title']}", callback_data=f"del_ebook_{e['id']}")])
    for p in db.list_podcasts():
        buttons.append([InlineKeyboardButton(f"🎙️ {p['title']}", callback_data=f"del_podcast_{p['id']}")])
    for s in db.list_sessions():
        buttons.append([InlineKeyboardButton(f"📅 {s['title']}", callback_data=f"del_session_{s['id']}")])
    buttons.append([InlineKeyboardButton("🔙 Voltar", callback_data="menu_admin")])
    return InlineKeyboardMarkup(buttons)


# CONVERSAS ADMIN — EBOOK

@admin_only
async def admin_add_ebook_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"{CEDRO_HEADER}📚 *Adicionar eBook*\n\nDigite o *título* do eBook:",
        parse_mode=ParseMode.MARKDOWN, reply_markup=cancel_kb()
    )
    return ADD_EBOOK_TITLE

async def ebook_title(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["ebook_title"] = update.message.text.strip()
    await update.message.reply_text("✏️ Agora envie uma *descrição breve*:", parse_mode=ParseMode.MARKDOWN)
    return ADD_EBOOK_DESC

async def ebook_desc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["ebook_desc"] = update.message.text.strip()
    await update.message.reply_text("📎 Envie o arquivo *PDF* do eBook:", parse_mode=ParseMode.MARKDOWN)
    return ADD_EBOOK_FILE

async def ebook_file(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text("⚠️ Por favor, envie um arquivo PDF.")
        return ADD_EBOOK_FILE
    file_id = update.message.document.file_id
    db.add_ebook(ctx.user_data["ebook_title"], ctx.user_data["ebook_desc"], file_id)
    await update.message.reply_text(
        f"✅ eBook *{ctx.user_data['ebook_title']}* adicionado com sucesso!",
        parse_mode=ParseMode.MARKDOWN
    )
    ctx.user_data.clear()
    return ConversationHandler.END


# CONVERSAS ADMIN — PODCAST

@admin_only
async def admin_add_podcast_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"{CEDRO_HEADER}🎙️ *Adicionar Podcast*\n\nDigite o *título* do episódio:",
        parse_mode=ParseMode.MARKDOWN, reply_markup=cancel_kb()
    )
    return ADD_PODCAST_TITLE

async def podcast_title(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["podcast_title"] = update.message.text.strip()
    await update.message.reply_text("✏️ Envie uma *descrição breve*:", parse_mode=ParseMode.MARKDOWN)
    return ADD_PODCAST_DESC

async def podcast_desc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["podcast_desc"] = update.message.text.strip()
    await update.message.reply_text("🎵 Envie o arquivo de *áudio* do podcast (MP3/OGG):", parse_mode=ParseMode.MARKDOWN)
    return ADD_PODCAST_FILE

async def podcast_file(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.audio and not update.message.voice and not update.message.document:
        await update.message.reply_text("⚠️ Por favor, envie um arquivo de áudio.")
        return ADD_PODCAST_FILE
    file_id = (update.message.audio or update.message.voice or update.message.document).file_id
    db.add_podcast(ctx.user_data["podcast_title"], ctx.user_data["podcast_desc"], file_id)
    await update.message.reply_text(
        f"✅ Podcast *{ctx.user_data['podcast_title']}* adicionado com sucesso!",
        parse_mode=ParseMode.MARKDOWN
    )
    ctx.user_data.clear()
    return ConversationHandler.END


# CONVERSAS ADMIN — SESSÃO

@admin_only
async def admin_add_session_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"{CEDRO_HEADER}📅 *Agendar Sessão em Grupo*\n\nDigite o *título* da sessão:",
        parse_mode=ParseMode.MARKDOWN, reply_markup=cancel_kb()
    )
    return ADD_SESSION_TITLE

async def session_title(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["session_title"] = update.message.text.strip()
    await update.message.reply_text(
        "🗓️ Informe a *data e horário* da sessão:\nFormato: `DD/MM/AAAA HH:MM`\nExemplo: `25/12/2025 19:00`",
        parse_mode=ParseMode.MARKDOWN
    )
    return ADD_SESSION_DATE

async def session_date(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    raw = update.message.text.strip()
    try:
        dt = datetime.strptime(raw, "%d/%m/%Y %H:%M")
        ctx.user_data["session_date"] = dt.strftime("%d/%m/%Y às %H:%M")
        await update.message.reply_text(
            "🔗 Envie o *link* da chamada (Google Meet, Zoom, etc.):",
            parse_mode=ParseMode.MARKDOWN
        )
        return ADD_SESSION_LINK
    except ValueError:
        await update.message.reply_text("⚠️ Formato inválido. Use `DD/MM/AAAA HH:MM`.", parse_mode=ParseMode.MARKDOWN)
        return ADD_SESSION_DATE

async def session_link(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.strip()
    db.add_session(ctx.user_data["session_title"], ctx.user_data["session_date"], link)
    await update.message.reply_text(
        f"✅ Sessão *{ctx.user_data['session_title']}* agendada para {ctx.user_data['session_date']}!",
        parse_mode=ParseMode.MARKDOWN
    )
    # Notifica todos os usuários
    users = db.list_users()
    text = (
        f"🌿 *CEDRO* | Nova Sessão em Grupo!\n\n"
        f"📅 *{ctx.user_data['session_title']}*\n"
        f"🗓️ {ctx.user_data['session_date']}\n"
        f"🔗 [Clique aqui para entrar]({link})"
    )
    for uid in users:
        try:
            await ctx.bot.send_message(uid, text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        except Exception:
            pass
    ctx.user_data.clear()
    return ConversationHandler.END


# CALLBACKS INLINE → INICIA CONVERSA

async def admin_inline_trigger(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    if not is_admin(uid):
        return
    data = query.data
    # Envia mensagem nova para iniciar o ConversationHandler via /comando
    if data == "admin_add_ebook":
        await query.message.reply_text(
            "📚 Use o comando /addebook para adicionar um eBook."
        )
    elif data == "admin_add_podcast":
        await query.message.reply_text(
            "🎙️ Use o comando /addpodcast para adicionar um podcast."
        )
    elif data == "admin_add_session":
        await query.message.reply_text(
            "📅 Use o comando /addsessao para agendar uma sessão."
        )

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("❌ Operação cancelada.")
    else:
        await update.message.reply_text("❌ Operação cancelada.")
    ctx.user_data.clear()
    return ConversationHandler.END


# COMANDOS DIRETOS DE LISTAGEM

async def cmd_ebooks(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ebooks = db.list_ebooks()
    if not ebooks:
        await update.message.reply_text(f"{CEDRO_HEADER}📚 Nenhum eBook disponível.", parse_mode=ParseMode.MARKDOWN)
        return
    buttons = [[InlineKeyboardButton(f"📄 {e['title']}", callback_data=f"ebook_{e['id']}")] for e in ebooks]
    await update.message.reply_text(
        f"{CEDRO_HEADER}📚 *eBooks Disponíveis:*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def cmd_podcasts(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    podcasts = db.list_podcasts()
    if not podcasts:
        await update.message.reply_text(f"{CEDRO_HEADER}🎙️ Nenhum podcast disponível.", parse_mode=ParseMode.MARKDOWN)
        return
    buttons = [[InlineKeyboardButton(f"▶️ {p['title']}", callback_data=f"podcast_{p['id']}")] for p in podcasts]
    await update.message.reply_text(
        f"{CEDRO_HEADER}🎙️ *Podcasts:*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def cmd_sessions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    sessions = db.list_sessions()
    if not sessions:
        await update.message.reply_text(f"{CEDRO_HEADER}📅 Nenhuma sessão agendada.", parse_mode=ParseMode.MARKDOWN)
        return
    text = f"{CEDRO_HEADER}📅 *Sessões Agendadas:*\n\n"
    for s in sessions:
        text += f"🟢 *{s['title']}*\n   🗓️ {s['date_str']}\n   🔗 [Entrar]({s['link']})\n\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

async def cmd_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Acesso negado.")
        return
    await update.message.reply_text(
        f"{CEDRO_HEADER}⚙️ *Painel Administrativo*\n\nEscolha uma ação:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=admin_menu_kb()
    )


# MAIN

def main():
    db.init()
    app = Application.builder().token(TOKEN).build()

    # ConversationHandler — eBook
    ebook_conv = ConversationHandler(
        entry_points=[CommandHandler("addebook", admin_add_ebook_start)],
        states={
            ADD_EBOOK_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ebook_title)],
            ADD_EBOOK_DESC:  [MessageHandler(filters.TEXT & ~filters.COMMAND, ebook_desc)],
            ADD_EBOOK_FILE:  [MessageHandler(filters.Document.ALL, ebook_file)],
        },
        fallbacks=[CommandHandler("cancelar", cancel), CallbackQueryHandler(cancel, pattern="^cancel_conv$")],
    )

    # ConversationHandler — Podcast
    podcast_conv = ConversationHandler(
        entry_points=[CommandHandler("addpodcast", admin_add_podcast_start)],
        states={
            ADD_PODCAST_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, podcast_title)],
            ADD_PODCAST_DESC:  [MessageHandler(filters.TEXT & ~filters.COMMAND, podcast_desc)],
            ADD_PODCAST_FILE:  [MessageHandler(filters.AUDIO | filters.VOICE | filters.Document.ALL, podcast_file)],
        },
        fallbacks=[CommandHandler("cancelar", cancel), CallbackQueryHandler(cancel, pattern="^cancel_conv$")],
    )

    # ConversationHandler — Sessão
    session_conv = ConversationHandler(
        entry_points=[CommandHandler("addsessao", admin_add_session_start)],
        states={
            ADD_SESSION_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, session_title)],
            ADD_SESSION_DATE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, session_date)],
            ADD_SESSION_LINK:  [MessageHandler(filters.TEXT & ~filters.COMMAND, session_link)],
        },
        fallbacks=[CommandHandler("cancelar", cancel), CallbackQueryHandler(cancel, pattern="^cancel_conv$")],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ajuda", help_cmd))
    app.add_handler(CommandHandler("ebooks", cmd_ebooks))
    app.add_handler(CommandHandler("podcasts", cmd_podcasts))
    app.add_handler(CommandHandler("sessoes", cmd_sessions))
    app.add_handler(CommandHandler("admin", cmd_admin))
    app.add_handler(ebook_conv)
    app.add_handler(podcast_conv)
    app.add_handler(session_conv)
    app.add_handler(CallbackQueryHandler(admin_inline_trigger, pattern="^admin_(add_ebook|add_podcast|add_session)$"))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("🌿 Bot CEDRO iniciado!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()