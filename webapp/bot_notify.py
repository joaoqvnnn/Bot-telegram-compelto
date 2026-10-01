# webapp/bot_notify.py
"""
Envia mensagens para o usuário no chat do bot
(direto pela Bot API, sem precisar do aiogram rodando).
"""
import logging
import httpx

from config import BOT_TOKEN

log = logging.getLogger(__name__)
API = f"https://api.telegram.org/bot{BOT_TOKEN}"


async def enviar_mensagem(user_id: int, texto: str, botao_url: str | None = None):
    payload = {
        "chat_id": user_id,
        "text": texto,
        "parse_mode": "HTML",
    }
    if botao_url:
        payload["reply_markup"] = {
            "inline_keyboard": [[{"text": "🔓 Ver produto", "url": botao_url}]]
        }
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(f"{API}/sendMessage", json=payload)
            if r.status_code != 200:
                log.warning("Bot API: %s", r.text)
        except Exception as e:
            log.exception("Erro ao notificar: %s", e)


async def notificar_compra_webapp(user_id: int, compra: dict, bot_username: str):
    """Envia mensagem de entrega no chat do bot depois da compra na loja."""
    from texts import texto_entrega  # importa o texto do bot
    try:
        txt = texto_entrega(compra)
    except Exception:
        txt = (
            f"✅ <b>Produto realizado com sucesso!</b>\n\n"
            f"🎫 ID: <code>{compra['id']}</code>\n"
            f"🚀 <b>{compra['produto_nome']}</b>\n"
            f"💰 Valor: <b>R$ {compra['valor_total']:.2f}</b>"
        )
    link = f"https://t.me/{bot_username}?start=ver_{compra['id']}"
    await enviar_mensagem(user_id, txt, botao_url=link)
