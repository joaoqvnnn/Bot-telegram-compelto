# handlers/top.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from database import (
    top_servicos, top_recargas, top_compras, top_giftcards, top_saldo,
    get_saldo,
)
from keyboards import kb_top, kb_menu
from texts import texto_top_compradores, boas_vindas

router = Router()

_FN = {
    "servicos": top_servicos,
    "recargas": top_recargas,
    "compras":  top_compras,
    "gifts":    top_giftcards,
    "saldo":    top_saldo,
}


async def _render(call: CallbackQuery, filtro: str):
    ranking = _FN.get(filtro, top_servicos)()
    texto = texto_top_compradores(filtro, ranking)

    # ⚠️ Regra: troca de filtro EDITA apenas o check verde
    try:
        await call.message.edit_text(
            texto,
            reply_markup=kb_top(filtro),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        await call.message.answer(
            texto,
            reply_markup=kb_top(filtro),
            parse_mode="HTML",
        )


@router.callback_query(F.data == "menu_top")
async def abrir_top(call: CallbackQuery):
    await _render(call, "servicos")
    await call.answer()


@router.callback_query(F.data.startswith("top:"))
async def trocar_filtro(call: CallbackQuery):
    filtro = call.data.split(":")[1]
    await _render(call, filtro)
    await call.answer()


@router.callback_query(F.data == "top_voltar")
async def top_voltar(call: CallbackQuery):
    try:
        await call.message.edit_text(
            boas_vindas(call.from_user.id, get_saldo(call.from_user.id)),
            reply_markup=kb_menu(),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        pass
    await call.answer()
