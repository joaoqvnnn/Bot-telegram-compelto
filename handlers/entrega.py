# handlers/entrega.py
from datetime import datetime

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from database import (
    debitar_saldo, decrementar_estoque, pegar_credencial,
    criar_compra, get_compra, get_user,
)
from keyboards import kb_entrega
from texts import texto_entrega
from utils.notificacoes import notificar_acesso

router = Router()


# ============================================================
# Helper — nome legível do usuário (para notificação)
# ============================================================
def _nome_ou_id(user_id: int) -> str:
    u = get_user(user_id) or {}
    return u.get("first_name") or u.get("username") or f"ID {user_id}"


# ============================================================
# Núcleo — processa entrega (chamado por 5.1 / 5B / 5.3)
# ============================================================
def processar_entrega(user_id: int, produto: dict, quantidade: int) -> dict | None:
    """Debita saldo, decrementa estoque, cria compra e retorna o dict da compra."""
    cred = pegar_credencial(produto["id"])
    if not cred:
        return None

    valor_total = produto["preco"] * quantidade

    debitar_saldo(user_id, valor_total)
    decrementar_estoque(produto["id"], quantidade)

    compra_id = criar_compra(
        user_id=user_id,
        produto_id=produto["id"],
        produto_nome=produto["nome"],
        quantidade=quantidade,
        valor_total=valor_total,
        email=cred["email"],
        senha=cred["senha"],
    )
    return get_compra(compra_id)


async def mostrar_entrega(msg, compra: dict, bot=None):
    """EDITS a msg informada com o texto de entrega."""
    try:
        await msg.edit_text(
            texto_entrega(compra),
            reply_markup=kb_entrega(compra["id"]),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        await msg.answer(
            texto_entrega(compra),
            reply_markup=kb_entrega(compra["id"]),
            parse_mode="HTML",
        )

    # 🔔 Notificação no canal
    if bot is not None:
        await notificar_acesso(
            bot=bot,
            user_id=compra["user_id"],
            user_nome=_nome_ou_id(compra["user_id"]),
            produto_nome=compra["produto_nome"],
            compra_id=compra["id"],
        )


# ============================================================
# 🔓 VER PRODUTO — edita msg revelando email/senha
# ============================================================
@router.callback_query(F.data.startswith("ent_revelar:"))
async def revelar(call: CallbackQuery):
    cid = int(call.data.split(":")[1])
    compra = get_compra(cid)
    if not compra or compra["user_id"] != call.from_user.id:
        await call.answer("Compra não encontrada.", show_alert=True)
        return

    try:
        await call.message.edit_text(
            texto_entrega(compra, revelar=True),
            reply_markup=kb_entrega(cid),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        pass
    await call.answer("🔓 Dados revelados!")


# ============================================================
# 🔗 CLIQUE AQUI PARA ATIVAR — stub (link externo configurável depois)
# ============================================================
@router.callback_query(F.data.startswith("ent_ativar:"))
async def ativar(call: CallbackQuery):
    await call.answer("🔗 Link de ativação será configurado no Admin.", show_alert=True)
