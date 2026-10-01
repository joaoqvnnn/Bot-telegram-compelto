# utils/rastreador.py
import asyncio
import logging
from datetime import datetime

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

from database import (
    get_config,
    carrinhos_abandonados, marcar_carrinho_notificado,
    pagamentos_expirados, marcar_pagamento_expirado,
    campanhas_pendentes, marcar_campanha_enviada, get_campanha,
)

log = logging.getLogger(__name__)
INTERVALO = 60  # segundos


def _link(bot_username: str, payload: str) -> str:
    return f"https://t.me/{bot_username}?start={payload}"


# ---------- Mensagens padrão (editáveis via Admin depois) ----------
def _texto_carrinho(produto_nome: str, produto_preco: float) -> str:
    return (
        "👋 <b>Ei, você esqueceu algo!</b>\n\n"
        f"Notamos que você estava olhando o produto <b>{produto_nome}</b> "
        "mas não finalizou a compra.\n\n"
        f"💰 Valor: <b>R$ {produto_preco:.2f}</b>\n\n"
        "🎁 <b>Que tal finalizar agora?</b>\n"
        "Seu produto está esperando por você!\n\n"
        "Se tiver alguma dúvida, estamos aqui para ajudar!"
    )


def _texto_pix_expirado(valor: float) -> str:
    return (
        "⏰ <b>Seu pagamento expirou!</b>\n\n"
        f"Vimos que você gerou um PIX de <b>R$ {valor:.2f}</b> mas não conseguiu finalizar.\n\n"
        "🤔 Aconteceu algum problema?\n\n"
        "Se precisar, você pode gerar um novo pagamento a qualquer momento. Estamos aqui para ajudar!\n\n"
        "💡 <b>Dica:</b> O PIX é instantâneo e a liberação é automática!"
    )


# ---------- Envio carrinho abandonado ----------
async def _enviar_carrinho(bot: Bot, bot_username: str, c: dict):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🛒 Finalizar agora",
            url=_link(bot_username, f"prod_{c['produto_id']}"),
        )],
        [InlineKeyboardButton(text="🏠 Menu Principal", url=_link(bot_username, "menu"))],
    ])
    try:
        await bot.send_message(
            c["user_id"],
            _texto_carrinho(c["produto_nome"], float(c["produto_preco"])),
            reply_markup=kb,
            parse_mode="HTML",
        )
        marcar_carrinho_notificado(c["id"])
    except TelegramBadRequest:
        # usuário bloqueou o bot
        marcar_carrinho_notificado(c["id"])


# ---------- Envio PIX expirado ----------
async def _enviar_pix_expirado(bot: Bot, bot_username: str, p: dict):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💠 Fazer Recarga", url=_link(bot_username, "recarga"))],
        [InlineKeyboardButton(text="🏠 Menu Principal", url=_link(bot_username, "menu"))],
    ])
    try:
        await bot.send_message(
            p["user_id"],
            _texto_pix_expirado(float(p["valor"])),
            reply_markup=kb,
            parse_mode="HTML",
        )
        marcar_pagamento_expirado(p["txid"])
    except TelegramBadRequest:
        marcar_pagamento_expirado(p["txid"])


# ---------- Envio campanha agendada ----------
async def _enviar_campanha(bot: Bot, camp: dict):
    import json
    botoes = json.loads(camp["botoes_json"] or "[]")
    rows = []
    for b in botoes:
        if b.get("url"):
            btn = InlineKeyboardButton(text=b["texto"], url=b["url"])
        else:
            me = await bot.get_me()
            btn = InlineKeyboardButton(
                text=b["texto"],
                url=_link(me.username, b.get("payload", "menu")),
            )
        rows.append([btn])
    kb = InlineKeyboardMarkup(inline_keyboard=rows) if rows else None

    canal = camp.get("canal") or get_config("canal_notificacoes", "")
    if not canal:
        log.warning("Campanha %s sem canal configurado", camp["id"])
        marcar_campanha_enviada(camp["id"])
        return

    try:
        if camp.get("foto_url"):
            await bot.send_photo(canal, camp["foto_url"], caption=camp["texto"],
                                 reply_markup=kb, parse_mode="HTML")
        else:
            await bot.send_message(canal, camp["texto"], reply_markup=kb, parse_mode="HTML")
        marcar_campanha_enviada(camp["id"])
    except TelegramBadRequest as e:
        log.warning("Falha ao enviar campanha %s: %s", camp["id"], e)
        marcar_campanha_enviada(camp["id"])


# ---------- Loop principal ----------
async def loop_rastreador(bot: Bot):
    log.info("🔎 Rastreador iniciado")
    while True:
        try:
            me = await bot.get_me()

            # 1) Carrinhos abandonados
            if get_config("carrinho_ativo", "1") == "1":
                minutos = int(get_config("carrinho_minutos", "20"))
                for c in carrinhos_abandonados(minutos):
                    await _enviar_carrinho(bot, me.username, c)
                    await asyncio.sleep(0.2)

            # 2) PIX expirados
            if get_config("pix_expirado_ativo", "1") == "1":
                for p in pagamentos_expirados():
                    await _enviar_pix_expirado(bot, me.username, p)
                    await asyncio.sleep(0.2)

            # 3) Campanhas agendadas
            for camp in campanhas_pendentes():
                await _enviar_campanha(bot, camp)
                await asyncio.sleep(0.2)

        except Exception as e:
            log.exception("Erro no rastreador: %s", e)

        await asyncio.sleep(INTERVALO)
