# utils/notificacoes.py
import logging
from datetime import datetime

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

from database import get_canal_notificacoes

log = logging.getLogger(__name__)


def _link_bot(bot_username: str, payload: str = "") -> str:
    base = f"https://t.me/{bot_username}"
    return f"{base}?start={payload}" if payload else base


async def notificar_estoque(bot: Bot, produto: dict):
    """🟢 Produto Abastecido! → envia no canal de notificações."""
    canal = get_canal_notificacoes()
    if not canal:
        return

    me = await bot.get_me()
    url_produto = _link_bot(me.username, f"prod_{produto['id']}")

    texto = (
        "🟢 <b>Produto Abastecido!</b>\n"
        f"<b>Nome:</b> {produto['nome']}\n"
        f"<b>Valor:</b> R$ {produto['preco']:.2f}\n"
        f"<b>Estoque:</b> {produto['estoque']}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Ver Produto", url=url_produto)],
    ])
    try:
        await bot.send_message(canal, texto, reply_markup=kb, parse_mode="HTML")
    except TelegramBadRequest as e:
        log.warning("Falha ao notificar estoque: %s", e)


async def notificar_acesso(
    bot: Bot,
    user_id: int,
    user_nome: str,
    produto_nome: str,
    compra_id: int | None = None,
):
    """💎 NOVO ACESSO LIBERADO → envia no canal de notificações."""
    canal = get_canal_notificacoes()
    if not canal:
        return

    me = await bot.get_me()
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    texto = (
        "💎 <b>NOVO ACESSO LIBERADO</b>\n"
        f"👤 <b>Usuário:</b> {user_nome} (ID {user_id})\n"
        f"📦 <b>Plano:</b> {produto_nome}\n"
        "💵 <b>Status:</b> ✅ Pago e ativo\n"
        f"🕐 <b>Data:</b> {agora}\n\n"
        "🚀 Acesso liberado automaticamente!"
    )

    rows = [[InlineKeyboardButton(text="🚀 Ir para o Bot", url=_link_bot(me.username))]]

    if compra_id:
        # Deep link — só quem comprou ou admin consegue ver
        url_ver = _link_bot(me.username, f"ver_{compra_id}")
        rows.append([InlineKeyboardButton(text="🔍 Ver Compra", url=url_ver)])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)

    try:
        await bot.send_message(canal, texto, reply_markup=kb, parse_mode="HTML")
    except TelegramBadRequest as e:
        log.warning("Falha ao notificar acesso: %s", e)
