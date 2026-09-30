# handlers/senha_saque.py
import re

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ForceReply
from aiogram.exceptions import TelegramBadRequest

from database import set_senha, get_user
from keyboards import kb_sem_senha, kb_menu
from texts import texto_cadastrar_senha_pedir, texto_cadastrar_senha_ok, boas_vindas

router = Router()


class SenhaFlow(StatesGroup):
    aguardando_senha = State()


@router.callback_query(F.data == "senha_cad")
async def cad_abrir(call: CallbackQuery, state: FSMContext):
    await state.set_state(SenhaFlow.aguardando_senha)
    try:
        await call.message.edit_text(
            texto_cadastrar_senha_pedir(),
            reply_markup=None,
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        pass
    await call.message.answer(
        "👇 Envie sua senha de 6 dígitos:",
        reply_markup=ForceReply(selective=True),
    )
    await call.answer()


@router.message(StateFilter(SenhaFlow.aguardando_senha), Command("cancelar"))
async def cad_cancel_cmd(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Operação cancelada.")


@router.message(StateFilter(SenhaFlow.aguardando_senha))
async def cad_receber(msg: Message, state: FSMContext):
    texto = (msg.text or "").strip()
    if not re.fullmatch(r"\d{6}", texto):
        await msg.answer("❌ A senha deve conter exatamente 6 dígitos numéricos.")
        return

    set_senha(msg.from_user.id, texto)
    await state.clear()

    # Apaga a msg com a senha (privacidade)
    try:
        await msg.delete()
    except Exception:
        pass

    u = get_user(msg.from_user.id) or {}
    await msg.answer(
        texto_cadastrar_senha_ok(),
        reply_markup=kb_sem_senha(),
        parse_mode="HTML",
    )
