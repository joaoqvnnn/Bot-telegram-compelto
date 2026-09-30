# handlers/catalogo.py
import asyncio

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, BufferedInputFile

from database import (
    get_saldo, get_produto, listar_produtos, get_pagamento, marcar_pago,
)
from keyboards import (
    kb_menu, kb_catalogo, kb_produto, kb_saldo_insuficiente, kb_qr_pix,
)
from texts import (
    boas_vindas, texto_catalogo, texto_produto, texto_saldo_insuficiente,
    texto_gerando_pagamento, texto_qr_pix, texto_aguardando_nao_pago, texto_pago,
)
from utils.pix import gerar_pix_qr
from handlers.entrega import processar_entrega, mostrar_entrega

router = Router()


# ---------- helper: edita com fallback ----------
async def _safe_edit(msg, text: str, markup=None):
    try:
        await msg.edit_text(text, reply_markup=markup, parse_mode="HTML")
    except TelegramBadRequest:
        await msg.answer(text, reply_markup=markup, parse_mode="HTML")


async def _safe_edit_caption(msg, text: str, markup=None):
    try:
        await msg.edit_caption(caption=text, reply_markup=markup, parse_mode="HTML")
    except TelegramBadRequest:
        await msg.answer(text, reply_markup=markup, parse_mode="HTML")


# ============================================================
# 📦 3. CATÁLOGO
# ============================================================
@router.callback_query(F.data == "menu_catalogo")
async def abrir_catalogo(call: CallbackQuery):
    saldo = get_saldo(call.from_user.id)
    produtos = listar_produtos()
    await _safe_edit(call.message, texto_catalogo(saldo), kb_catalogo(produtos))
    await call.answer()


@router.callback_query(F.data == "cat_voltar_menu")
async def cat_voltar_menu(call: CallbackQuery):
    saldo = get_saldo(call.from_user.id)
    await _safe_edit(call.message, boas_vindas(call.from_user.id, saldo), kb_menu())
    await call.answer()


# ============================================================
# 🎯 4. TELA DO PRODUTO
# ============================================================
@router.callback_query(F.data.startswith("prod:"))
async def abrir_produto(call: CallbackQuery):
    pid = int(call.data.split(":")[1])
    produto = get_produto(pid)
    if not produto:
        await call.answer("Produto não encontrado.", show_alert=True)
        return

    saldo = get_saldo(call.from_user.id)
    await _safe_edit(call.message, texto_produto(produto, saldo), kb_produto(pid))
    await call.answer()


@router.callback_query(F.data == "prod_voltar_catalogo")
async def prod_voltar_catalogo(call: CallbackQuery):
    saldo = get_saldo(call.from_user.id)
    produtos = listar_produtos()
    await _safe_edit(call.message, texto_catalogo(saldo), kb_catalogo(produtos))
    await call.answer()


# ============================================================
# 💸 5.1 COMPRAR — sempre NOVA MSG
# ============================================================
@router.callback_query(F.data.startswith("prod_buy:"))
async def comprar(call: CallbackQuery, bot: Bot):
    pid = int(call.data.split(":")[1])
    produto = get_produto(pid)
    if not produto:
        await call.answer("Produto não encontrado.", show_alert=True)
        return
    if produto["estoque"] <= 0:
        await call.answer("❌ Sem estoque disponível.", show_alert=True)
        return

    saldo = get_saldo(call.from_user.id)

    # -------- Caso 1: saldo suficiente → NOVA MSG e depois entrega --------
    if saldo >= produto["preco"]:
        msg = await call.message.answer(
            f"✅ <b>Compra aprovada!</b>\n\n"
            f"🚀 <b>{produto['nome']}</b>\n"
            f"💵 Valor: <b>R$ {produto['preco']:.2f}</b>\n"
            f"💰 Saldo restante: <b>R$ {saldo - produto['preco']:.2f}</b>\n\n"
            f"⏳ Preparando sua entrega...",
            parse_mode="HTML",
        )
        await call.answer()

        compra = processar_entrega(call.from_user.id, produto, 1)
        if not compra:
            await msg.edit_text("❌ Sem credenciais em estoque.")
            return

        await asyncio.sleep(1)
        await mostrar_entrega(msg, compra)   # EDITA a msg de confirmação → entrega
        return

    # -------- Caso 2: saldo insuficiente → NOVA MSG --------
    faltam = produto["preco"] - saldo
    await call.message.answer(
        texto_saldo_insuficiente(saldo, produto["preco"], faltam),
        reply_markup=kb_saldo_insuficiente(pid, produto["preco"]),
        parse_mode="HTML",
    )
    # ⚠️ A mensagem original do produto PERMANECE no chat.
    await call.answer()


# ============================================================
# 💠 5.2 GERAR PIX — EDITA msg → "Gerando..." → 2s → NOVA MSG com QR
# ============================================================
@router.callback_query(F.data.startswith("pix_gen:"))
async def gerar_pix(call: CallbackQuery):
    _, pid_s, valor_s = call.data.split(":")
    pid = int(pid_s)
    valor = float(valor_s)

    # 1) EDITA a msg "Saldo insuficiente" → "Gerando pagamento..."
    try:
        await call.message.edit_text(texto_gerando_pagamento(), parse_mode="HTML")
    except TelegramBadRequest:
        pass

    # 2) Gera PIX (placeholder)
    txid, copia_cola, qr_bytes = gerar_pix_qr(call.from_user.id, pid, valor)

    # 3) Delay de 2s
    await asyncio.sleep(2)

    # 4) NOVA MSG com imagem + botões
    await call.message.answer_photo(
        photo=BufferedInputFile(qr_bytes, filename=f"pix_{txid}.png"),
        caption=texto_qr_pix(valor, txid),
        reply_markup=kb_qr_pix(txid, copia_cola),
        parse_mode="HTML",
    )
    await call.answer()


# ============================================================
# ⏰ 5.3 AGUARDANDO PAGAMENTO
# ============================================================
@router.callback_query(F.data.startswith("pix_wait:"))
async def pix_wait(call: CallbackQuery):
    txid = call.data.split(":")[1]
    pag = get_pagamento(txid)
    if not pag:
        await call.answer("Pagamento não encontrado.", show_alert=True)
        return

    # -------- Não pago → NOVA MSG de aviso --------
    if pag["status"] != "pago":
        await call.message.answer(texto_aguardando_nao_pago(), parse_mode="HTML")
        await call.answer()
        return

    # -------- Pago → EDITA QR atual p/ verde ✅ PAGO --------
    await _safe_edit_caption(call.message, texto_pago(), markup=None)

    # -------- EDITA novamente p/ entrega (Seção 6) --------
    await asyncio.sleep(1)

    produto = get_produto(pag["produto_id"]) if pag["produto_id"] else None
    if produto:
        # credita o valor pago e debita em seguida (simulação até integrar webhook)
        marcar_pago(txid)
        compra = processar_entrega(call.from_user.id, produto, 1)
        if compra:
            await mostrar_entrega(call.message, compra)
            await call.answer()
            return

    await _safe_edit_caption(
        call.message,
        "✅ <b>Produto realizado com sucesso!</b>\n\n<i>(Entrega pendente.)</i>",
        markup=None,
    )
    await call.answer()


# ============================================================
# ❌ 5.4 CANCELAR (na msg de Saldo Insuficiente) → volta ao /start
# ============================================================
@router.callback_query(F.data.startswith("pix_cancel:"))
async def pix_cancel(call: CallbackQuery):
    saldo = get_saldo(call.from_user.id)
    await _safe_edit(call.message, boas_vindas(call.from_user.id, saldo), kb_menu())
    await call.answer()
