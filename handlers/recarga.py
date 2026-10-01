# handlers/recarga.py
import asyncio
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ForceReply, BufferedInputFile
from aiogram.exceptions import TelegramBadRequest

from database import (
    get_config, get_saldo, criar_recarga, get_recarga,
    marcar_recarga_paga, get_user,
)
from keyboards import (
    kb_recarga_menu, kb_recarga_pedir_valor, kb_recarga_qr, kb_recarga_ok,
    kb_menu,
)
from texts import (
    texto_recarga_menu, texto_recarga_pedir_valor,
    texto_recarga_qr, texto_recarga_ok, boas_vindas,
)
from utils.pix import gerar_pix_qr
from utils.notificacoes import notificar_acesso

router = Router()


class Recarga(StatesGroup):
    aguardando_valor = State()


# ---------- Menu ----------
@router.callback_query(F.data == "menu_recarga")
async def menu_recarga(call: CallbackQuery):
    try:
        await call.message.edit_text(
            texto_recarga_menu(),
            reply_markup=kb_recarga_menu(),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        pass
    await call.answer()


@router.callback_query(F.data == "rec_voltar")
async def rec_voltar(call: CallbackQuery):
    u = get_user(call.from_user.id) or {}
    try:
        await call.message.edit_text(
            boas_vindas(call.from_user.id, u.get("saldo", 0.0)),
            reply_markup=kb_menu(),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        pass
    await call.answer()


# ---------- PIX Rápido ----------
@router.callback_query(F.data == "rec_pix")
async def rec_pix(call: CallbackQuery, state: FSMContext):
    await state.set_state(Recarga.aguardando_valor)
    try:
        await call.message.edit_text(
            texto_recarga_pedir_valor(),
            reply_markup=kb_recarga_pedir_valor(),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        pass
    await call.message.answer(
        "👇 Envie o valor da recarga:",
        reply_markup=ForceReply(selective=True),
    )
    await call.answer()


# ---------- Cancelar (pedido valor) ----------
@router.message(StateFilter(Recarga.aguardando_valor), Command("cancelar"))
async def rec_cancel_cmd(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Recarga cancelada.")


@router.callback_query(F.data == "rec_cancel")
async def rec_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    u = get_user(call.from_user.id) or {}
    try:
        await call.message.edit_text(
            boas_vindas(call.from_user.id, u.get("saldo", 0.0)),
            reply_markup=kb_menu(),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        pass
    await call.answer()


# ---------- Recebe valor ----------
@router.message(StateFilter(Recarga.aguardando_valor))
async def rec_receber(msg: Message, state: FSMContext):
    texto = (msg.text or "").strip().replace(",", ".")
    try:
        valor = float(texto)
    except ValueError:
        await msg.answer("❌ Valor inválido. Envie apenas números (ex: 25.00).")
        return

    minimo = float(get_config("recarga_minima", "4.00"))
    if valor < minimo:
        await msg.answer(f"❌ Valor mínimo é R$ {minimo:.2f}.")
        return

    # Bônus
    bonus_ativo = get_config("recarga_bonus_ativo", "1") == "1"
    bonus_pct = float(get_config("recarga_bonus_pct", "10"))
    bonus_min = float(get_config("recarga_bonus_min", "10.00"))
    bonus = round(valor * bonus_pct / 100, 2) if (bonus_ativo and valor >= bonus_min) else 0.0

    await state.clear()

    # NOVA MSG ⏳ Gerando pagamento...
    gerando = await msg.answer("⏳ <b>Gerando pagamento...</b>", parse_mode="HTML")

    txid, copia_cola, qr_bytes = gerar_pix_qr(msg.from_user.id, 0, valor)
    criar_recarga(txid, msg.from_user.id, valor, bonus, copia_cola)

    await asyncio.sleep(2)
    await gerando.delete()

    saldo_atual = get_saldo(msg.from_user.id)
    await msg.answer_photo(
        photo=BufferedInputFile(qr_bytes, filename=f"rec_{txid}.png"),
        caption=texto_recarga_qr(valor, bonus, saldo_atual, txid),
        reply_markup=kb_recarga_qr(txid, copia_cola),
        parse_mode="HTML",
    )


# ---------- ⏰ AGUARDANDO PAGAMENTO ----------
@router.callback_query(F.data.startswith("rec_wait:"))
async def rec_wait(call: CallbackQuery):
    txid = call.data.split(":")[1]
    rec = get_recarga(txid)
    if not rec:
        await call.answer("Recarga não encontrada.", show_alert=True)
        return

    if rec["status"] != "pago":
        await call.message.answer(
            "⚠️ <b>Pagamento não identificado.</b>\n"
            "Se já pagou, aguarde alguns instantes e tente novamente.",
            parse_mode="HTML",
        )
        await call.answer()
        return

    # Já pago → marca e credita
    if marcar_recarga_paga(txid):
        try:
            await call.message.edit_caption(
                caption="✅ <b>PAGO</b>",
                parse_mode="HTML",
            )
        except TelegramBadRequest:
            pass

        # 🔔 Notificação no canal
        u = get_user(call.from_user.id) or {}
        await notificar_acesso(
            bot=call.bot,
            user_id=call.from_user.id,
            user_nome=u.get("first_name") or u.get("username") or f"ID {call.from_user.id}",
            produto_nome=f"Recarga de R$ {rec['valor']:.2f}",
            compra_id=None,
        )

        await asyncio.sleep(1)
        saldo_novo = get_saldo(call.from_user.id)
        await call.message.answer(
            texto_recarga_ok(rec["valor"], rec["bonus"] or 0, saldo_novo),
            reply_markup=kb_recarga_ok(),
            parse_mode="HTML",
        )
    await call.answer()


@router.callback_query(F.data.startswith("rec_cancel_qr:"))
async def rec_cancel_qr(call: CallbackQuery):
    u = get_user(call.from_user.id) or {}
    try:
        await call.message.edit_caption(caption="❌ Recarga cancelada.")
        await call.message.edit_reply_markup(reply_markup=None)
    except TelegramBadRequest:
        pass
    await call.message.answer(
        boas_vindas(call.from_user.id, u.get("saldo", 0.0)),
        reply_markup=kb_menu(),
        parse_mode="HTML",
    )
    await call.answer()
