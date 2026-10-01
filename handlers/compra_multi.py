# handlers/compra_multi.py
import asyncio

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ForceReply, BufferedInputFile
from aiogram.exceptions import TelegramBadRequest

from database import get_produto, get_saldo
from keyboards import kb_menu, kb_resultado_pedido, kb_saldo_insuficiente_multi, kb_qr_pix
from texts import (
    boas_vindas, texto_perguntar_qtd, texto_resultado_pedido,
    texto_saldo_insuficiente_multi, texto_compra_cancelada, texto_qtd_invalida,
    texto_gerando_pagamento, texto_qr_pix,
)
from utils.pix import gerar_pix_qr
from handlers.entrega import processar_entrega, mostrar_entrega

router = Router()


class BuyMulti(StatesGroup):
    aguardando_qtd = State()


# ============================================================
# Abrir fluxo — "🛒 Comprar mais de um"
# ============================================================
@router.callback_query(F.data.startswith("prod_buy_multi:"))
async def abrir_multi(call: CallbackQuery, state: FSMContext):
    pid = int(call.data.split(":")[1])
    produto = get_produto(pid)
    if not produto:
        await call.answer("Produto não encontrado.", show_alert=True)
        return
    if produto["estoque"] <= 0:
        await call.answer("❌ Sem estoque disponível.", show_alert=True)
        return

    await state.set_state(BuyMulti.aguardando_qtd)
    await state.update_data(pid=pid)

    await call.message.answer(
        texto_perguntar_qtd(produto["estoque"]),
        reply_markup=ForceReply(selective=True),
        parse_mode="HTML",
    )
    await call.answer()


# ============================================================
# /cancelar durante ForceReply
# ============================================================
@router.message(StateFilter(BuyMulti.aguardando_qtd), Command("cancelar"))
async def cancelar_multi(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(texto_compra_cancelada(), parse_mode="HTML")


# ============================================================
# Receber quantidade
# ============================================================
@router.message(StateFilter(BuyMulti.aguardando_qtd))
async def receber_qtd(msg: Message, state: FSMContext):
    data = await state.get_data()
    produto = get_produto(data["pid"])
    if not produto:
        await state.clear()
        return

    texto = (msg.text or "").strip()
    if not texto.isdigit():
        await msg.answer(texto_qtd_invalida(produto["estoque"]), parse_mode="HTML")
        return

    qtd = int(texto)
    if qtd < 1 or qtd > produto["estoque"]:
        await msg.answer(texto_qtd_invalida(produto["estoque"]), parse_mode="HTML")
        return

    total = produto["preco"] * qtd
    saldo = get_saldo(msg.from_user.id)
    await state.clear()

    # -------- Saldo SUFICIENTE --------
    if saldo >= total:
        await msg.answer(
            texto_resultado_pedido(produto, qtd, total, saldo),
            reply_markup=kb_resultado_pedido(produto["id"], qtd, total),
            parse_mode="HTML",
        )
        return

    # -------- Saldo INSUFICIENTE --------
    faltam = total - saldo
    await msg.answer(
        texto_saldo_insuficiente_multi(saldo, total, faltam),
        reply_markup=kb_saldo_insuficiente_multi(total),
        parse_mode="HTML",
    )


# ============================================================
# ✅ Confirmar Compra
# ============================================================
@router.callback_query(F.data.startswith("multi_conf:"))
async def confirmar_compra(call: CallbackQuery):
    _, pid_s, qtd_s, total_s = call.data.split(":")
    pid = int(pid_s)
    qtd = int(qtd_s)

    produto = get_produto(pid)
    if not produto:
        await call.answer("Produto não encontrado.", show_alert=True)
        return

    total = produto["preco"] * qtd
    saldo = get_saldo(call.from_user.id)
    if saldo < total:
        await call.answer("❌ Saldo insuficiente.", show_alert=True)
        return
    if produto["estoque"] < qtd:
        await call.answer("❌ Estoque insuficiente.", show_alert=True)
        return

    compra = processar_entrega(call.from_user.id, produto, qtd)
    if not compra:
        await call.answer("❌ Sem credenciais em estoque.", show_alert=True)
        return

    # EDITA a mensagem do resultado p/ a entrega (Seção 6) + notifica canal
    await mostrar_entrega(call.message, compra, bot=call.bot)
    await call.answer("✅ Compra confirmada!")


# ============================================================
# ❌ Cancelar (resultado do pedido OU saldo insuficiente)
# ============================================================
@router.callback_query(F.data == "multi_cancel")
async def cancelar(call: CallbackQuery):
    saldo = get_saldo(call.from_user.id)
    try:
        await call.message.edit_text(
            boas_vindas(call.from_user.id, saldo),
            reply_markup=kb_menu(),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        await call.message.answer(
            boas_vindas(call.from_user.id, saldo),
            reply_markup=kb_menu(),
            parse_mode="HTML",
        )
    await call.answer()


# ============================================================
# 💠 Gerar PIX — mesmo fluxo 5.2 (EDITA "Gerando..." → 2s → NOVA MSG com QR)
# ============================================================
@router.callback_query(F.data.startswith("multi_pix:"))
async def gerar_pix_multi(call: CallbackQuery):
    total = float(call.data.split(":")[1])

    try:
        await call.message.edit_text(texto_gerando_pagamento(), parse_mode="HTML")
    except TelegramBadRequest:
        pass

    # produto_id=0 pois é avulso (compra múltipla — vincula no gateway real)
    txid, copia_cola, qr_bytes = gerar_pix_qr(call.from_user.id, 0, total)

    await asyncio.sleep(2)

    await call.message.answer_photo(
        photo=BufferedInputFile(qr_bytes, filename=f"pix_{txid}.png"),
        caption=texto_qr_pix(total, txid),
        reply_markup=kb_qr_pix(txid, copia_cola),
        parse_mode="HTML",
    )
    await call.answer()
