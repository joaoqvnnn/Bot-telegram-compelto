# handlers/gift.py
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ForceReply
from aiogram.exceptions import TelegramBadRequest

from database import (
    get_gift, resgatar_gift, creditar_saldo, get_produto,
    get_user, get_saldo, estatisticas_usuario,
)
from keyboards import kb_gift_pedir, kb_gift_ok, kb_perfil
from texts import (
    texto_gift_pedir, texto_gift_invalido, texto_gift_ok, texto_perfil,
)

router = Router()


class GiftFlow(StatesGroup):
    aguardando = State()


def _render_perfil(user_id: int) -> str:
    u = get_user(user_id) or {}
    return texto_perfil(
        user_id, u.get("saldo", 0.0), u.get("whatsapp", ""),
        estatisticas_usuario(user_id),
    )


# ---------- Abrir (vem do perfil) ----------
@router.callback_query(F.data == "perfil_gift")
async def abrir_gift(call: CallbackQuery, state: FSMContext):
    await state.set_state(GiftFlow.aguardando)
    try:
        await call.message.edit_text(
            texto_gift_pedir(),
            reply_markup=kb_gift_pedir(),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        pass

    # Envia ForceReply como NOVA MSG curta para capturar input
    await call.message.answer(
        "👇 Envie o código:",
        reply_markup=ForceReply(selective=True),
    )
    await call.answer()


# ---------- /cancelar ----------
@router.message(StateFilter(GiftFlow.aguardando), Command("cancelar"))
async def gift_cancelar_cmd(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "❌ Operação cancelada.",
        reply_markup=None,
    )


# ---------- ❌ Cancelar (botão) — volta ao Perfil ----------
@router.callback_query(F.data == "gift_cancel")
async def gift_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await call.message.edit_text(
            _render_perfil(call.from_user.id),
            reply_markup=kb_perfil(),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        pass
    await call.answer()


@router.callback_query(F.data == "gift_voltar")
async def gift_voltar(call: CallbackQuery):
    try:
        await call.message.edit_text(
            _render_perfil(call.from_user.id),
            reply_markup=kb_perfil(),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        pass
    await call.answer()


# ---------- Recebe código ----------
@router.message(StateFilter(GiftFlow.aguardando))
async def gift_receber(msg: Message, state: FSMContext):
    codigo = (msg.text or "").strip().upper()
    if not codigo or codigo.startswith("/"):
        await msg.answer("❌ Envie um código válido.")
        return

    gift = get_gift(codigo)
    if not gift or gift["usado"]:
        # EDITA a msg principal (a que pediu o código) — aqui é NOVA MSG curta
        await msg.answer(texto_gift_invalido(), parse_mode="HTML")
        return

    resgatar_gift(codigo, msg.from_user.id)
    creditar_saldo(msg.from_user.id, gift["valor"])

    produto = get_produto(gift["produto_id"]) if gift["produto_id"] else None
    produto_nome = produto["nome"] if produto else None

    await msg.answer(
        texto_gift_ok(gift["valor"], produto_nome),
        reply_markup=kb_gift_ok(gift["produto_id"]),
        parse_mode="HTML",
    )
    await state.clear()
