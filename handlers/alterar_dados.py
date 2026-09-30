# handlers/alterar_dados.py
import re

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ForceReply
from aiogram.exceptions import TelegramBadRequest

from database import (
    get_user, set_whatsapp, estatisticas_usuario,
)
from keyboards import kb_alterar_dados, kb_perfil
from texts import (
    texto_alterar_dados_atual, texto_alterar_dados_invalido,
    texto_alterar_dados_ok, texto_perfil,
)

router = Router()


class AltDados(StatesGroup):
    aguardando_zap = State()


def _render_perfil(user_id: int) -> str:
    u = get_user(user_id) or {}
    return texto_perfil(
        user_id, u.get("saldo", 0.0), u.get("whatsapp", ""),
        estatisticas_usuario(user_id),
    )


# ---------- Abrir (vem do perfil) ----------
@router.callback_query(F.data == "perfil_alt")
async def abrir_alt(call: CallbackQuery, state: FSMContext):
    u = get_user(call.from_user.id) or {}
    await state.set_state(AltDados.aguardando_zap)

    try:
        await call.message.edit_text(
            texto_alterar_dados_atual(u.get("whatsapp", "")),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        pass

    await call.message.answer(
        "👇 Envie o novo número:",
        reply_markup=ForceReply(selective=True),
    )
    await call.answer()


# ---------- /cancelar ----------
@router.message(StateFilter(AltDados.aguardando_zap), Command("cancelar"))
async def alt_cancel_cmd(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Operação cancelada.")


# ---------- ❌ Cancelar (botão) ----------
@router.callback_query(F.data == "alt_cancel")
async def alt_cancel(call: CallbackQuery, state: FSMContext):
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


# ---------- Recebe número ----------
@router.message(StateFilter(AltDados.aguardando_zap))
async def alt_receber(msg: Message, state: FSMContext):
    texto = (msg.text or "").strip()

    # Bloqueia /start durante o fluxo
    if texto.startswith("/start"):
        await msg.answer("⚠️ Você está em um fluxo. Digite /cancelar para sair.")
        return

    if texto.lower() == "remover":
        set_whatsapp(msg.from_user.id, "")
        await state.clear()
        await msg.answer(
            texto_alterar_dados_ok(""),
            reply_markup=kb_perfil(),
            parse_mode="HTML",
        )
        return

    numeros = re.sub(r"\D", "", texto)
    # DDD + número → 10 ou 11 dígitos; DDD válido (11-99)
    if len(numeros) not in (10, 11) or not (11 <= int(numeros[:2]) <= 99):
        await msg.answer(texto_alterar_dados_invalido(), parse_mode="HTML")
        return

    set_whatsapp(msg.from_user.id, numeros)
    await state.clear()
    await msg.answer(
        texto_alterar_dados_ok(numeros),
        reply_markup=kb_perfil(),
        parse_mode="HTML",
    )
