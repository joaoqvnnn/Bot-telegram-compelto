# handlers/saques.py
import asyncio
import uuid
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ForceReply, BufferedInputFile
from aiogram.exceptions import TelegramBadRequest

from database import (
    get_saldo, get_senha_hash, get_chave_pix, set_chave_pix,
    criar_saque, debitar_saldo, get_user, listar_saques,
)
from keyboards import (
    kb_sem_senha, kb_pedir_chave, kb_confirma_chave,
    kb_valor_saque, kb_confirmar_saque, kb_comprovante, kb_menu,
)
from texts import (
    texto_sem_senha, texto_pedir_chave, texto_cadastrar_chave,
    texto_chave_invalida, texto_confirma_chave, texto_tela_saque,
    texto_pedir_valor_saque, texto_confirmar_saque, texto_pedir_senha,
    texto_senha_errada, texto_saque_processando, texto_saque_ok,
    boas_vindas,
)
from utils.validadores import (
    validar_cpf, validar_email, validar_telefone, validar_uuid, mascarar,
)
from utils.pix_consulta import consultar_chave
from utils.comprovante import gerar_comprovante_png, gerar_comprovante_pdf

router = Router()

SAQUE_MINIMO = 20.00


TIPO_LABEL = {
    "aleatoria": "Chave Aleatória",
    "cpf":       "CPF",
    "email":     "E-mail",
    "telefone":  "Telefone",
}


class SaqueFlow(StatesGroup):
    aguardando_chave   = State()
    aguardando_valor   = State()
    aguardando_senha   = State()


async def _safe_edit(msg, text, markup=None):
    try:
        await msg.edit_text(text, reply_markup=markup, parse_mode="HTML")
    except TelegramBadRequest:
        await msg.answer(text, reply_markup=markup, parse_mode="HTML")


def _nome(user_id: int) -> str:
    u = get_user(user_id) or {}
    return u.get("first_name") or u.get("username") or "Cliente"


# ============================================================
# 14. Entrada — chama por "💸 Saques"
# ============================================================
@router.callback_query(F.data == "af_saques")
async def entrar_saques(call: CallbackQuery, state: FSMContext):
    await state.clear()

    # 14.1 — sem senha
    if not get_senha_hash(call.from_user.id):
        await _safe_edit(call.message, texto_sem_senha(), kb_sem_senha())
        await call.answer()
        return

    # 14.2 — com senha, pede chave
    await _safe_edit(call.message, texto_pedir_chave(), kb_pedir_chave())
    await call.answer()


@router.callback_query(F.data == "saq_voltar")
async def saq_voltar(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await _safe_edit(
        call.message,
        boas_vindas(call.from_user.id, get_saldo(call.from_user.id)),
        kb_menu(),
    )
    await call.answer()


# ============================================================
# 14.3 — escolha do tipo de chave
# ============================================================
@router.callback_query(F.data.startswith("ck:"))
async def escolher_tipo(call: CallbackQuery, state: FSMContext):
    tipo = call.data.split(":")[1]
    label = TIPO_LABEL[tipo]

    await state.set_state(SaqueFlow.aguardando_chave)
    await state.update_data(tipo=tipo)

    await _safe_edit(call.message, texto_cadastrar_chave(label), None)
    await call.message.answer(
        f"👇 Envie seu {label}:",
        reply_markup=ForceReply(selective=True),
    )
    await call.answer()


@router.message(StateFilter(SaqueFlow.aguardando_chave), Command("cancelar"))
async def chave_cancel_cmd(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Operação cancelada.")


# ============================================================
# Validação + consulta da chave PIX
# ============================================================
@router.message(StateFilter(SaqueFlow.aguardando_chave))
async def receber_chave(msg: Message, state: FSMContext):
    data = await state.get_data()
    tipo = data.get("tipo")
    label = TIPO_LABEL[tipo]
    texto = (msg.text or "").strip()

    # Valida
    ok = False
    if tipo == "cpf":
        ok = validar_cpf(texto)
    elif tipo == "email":
        ok = validar_email(texto)
    elif tipo == "telefone":
        ok = validar_telefone(texto)
    elif tipo == "aleatoria":
        ok = validar_uuid(texto)

    if not ok:
        await msg.answer(texto_chave_invalida(label), parse_mode="HTML")
        return

    # Consulta titular
    info = await consultar_chave(tipo, texto)
    if not info:
        await msg.answer("❌ Não foi possível validar essa chave. Tente novamente.")
        return

    await state.update_data(chave=texto, titular_nome=info["nome"], titular_banco=info["banco"])
    await state.set_state(None)

    # EDITA msg atual com a confirmação
    await msg.answer(
        texto_confirma_chave(info["nome"], info["banco"], label, mascarar(tipo, texto)),
        reply_markup=kb_confirma_chave(),
        parse_mode="HTML",
    )


# ============================================================
# 14.4 — Confirmar / Editar chave
# ============================================================
@router.callback_query(F.data == "ck_conf")
async def confirmar_chave(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    tipo = data.get("tipo")
    if not tipo:
        await call.answer("Sessão expirada. Refaça o processo.", show_alert=True)
        return

    set_chave_pix(
        call.from_user.id, tipo, data["chave"],
        data["titular_nome"], data["titular_banco"],
    )

    # 14.5 — Tela de saque com saudação dinâmica
    saldo = get_saldo(call.from_user.id)
    await _safe_edit(
        call.message,
        texto_tela_saque(_nome(call.from_user.id), saldo, SAQUE_MINIMO),
        kb_valor_saque(),
    )
    await call.answer("✅ Chave confirmada!")


@router.callback_query(F.data == "ck_edit")
async def editar_chave(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    tipo = data.get("tipo") or "cpf"
    label = TIPO_LABEL[tipo]

    await state.set_state(SaqueFlow.aguardando_chave)
    await _safe_edit(call.message, texto_cadastrar_chave(label), None)
    await call.message.answer(
        f"👇 Envie novamente seu {label}:",
        reply_markup=ForceReply(selective=True),
    )
    await call.answer()


# ============================================================
# 14.5/14.6 — Valores sugeridos ou digitar
# ============================================================
@router.callback_query(F.data.startswith("sv:"))
async def valor_sugerido(call: CallbackQuery, state: FSMContext):
    valor = float(call.data.split(":")[1])
    await _confirmar_e_pedir_senha(call.message, call.from_user.id, valor, state)
    await call.answer()


@router.callback_query(F.data == "sv_dig")
async def digitar_valor(call: CallbackQuery, state: FSMContext):
    await state.set_state(SaqueFlow.aguardando_valor)
    saldo = get_saldo(call.from_user.id)
    await _safe_edit(call.message, texto_pedir_valor_saque(saldo, SAQUE_MINIMO), None)
    await call.message.answer(
        "👇 Envie o valor que deseja sacar:",
        reply_markup=ForceReply(selective=True),
    )
    await call.answer()


@router.message(StateFilter(SaqueFlow.aguardando_valor), Command("cancelar"))
async def valor_cancel_cmd(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Operação cancelada.")


@router.message(StateFilter(SaqueFlow.aguardando_valor))
async def valor_recebido(msg: Message, state: FSMContext):
    texto = (msg.text or "").strip().replace(",", ".")
    try:
        valor = float(texto)
    except ValueError:
        await msg.answer("❌ Valor inválido.")
        return

    saldo = get_saldo(msg.from_user.id)
    if valor < SAQUE_MINIMO:
        await msg.answer(f"❌ Saque mínimo é R$ {SAQUE_MINIMO:.2f}.")
        return
    if valor > saldo:
        await msg.answer(f"❌ Saldo insuficiente. Disponível: R$ {saldo:.2f}.")
        return

    # Apaga a msg do usuário (privacidade / regra 14.7 "EDITA apagando o valor digitado")
    try:
        await msg.delete()
    except Exception:
        pass

    await _confirmar_e_pedir_senha(msg, msg.from_user.id, valor, state)


async def _confirmar_e_pedir_senha(msg, user_id: int, valor: float, state: FSMContext):
    chave = get_chave_pix(user_id)
    if not chave:
        await msg.answer("❌ Chave PIX não encontrada. Refaça o processo.")
        return

    await state.update_data(valor=valor)

    texto = texto_confirmar_saque(
        chave["titular_nome"], chave["titular_banco"],
        mascarar(chave["tipo"], chave["chave"]), valor,
    )
    # se `msg` é Message (editável) → edita; se é CallbackQuery.message → também
    await _safe_edit(msg, texto, kb_confirmar_saque())


# ============================================================
# 14.7 — Confirmar / Cancelar Saque
# ============================================================
@router.callback_query(F.data == "sv_conf")
async def confirmar_saque(call: CallbackQuery, state: FSMContext):
    await state.set_state(SaqueFlow.aguardando_senha)
    await _safe_edit(call.message, texto_pedir_senha(), None)
    await call.message.answer(
        "👇 Envie sua senha:",
        reply_markup=ForceReply(selective=True),
    )
    await call.answer()


@router.callback_query(F.data == "sv_cancel")
async def cancelar_saque(call: CallbackQuery, state: FSMContext):
    await state.clear()
    # 14.10 — volta para a tela de saque (14.5)
    saldo = get_saldo(call.from_user.id)
    await _safe_edit(
        call.message,
        texto_tela_saque(_nome(call.from_user.id), saldo, SAQUE_MINIMO),
        kb_valor_saque(),
    )
    await call.answer()


# ============================================================
# 14.9 — Recebe senha e processa o saque
# ============================================================
@router.message(StateFilter(SaqueFlow.aguardando_senha), Command("cancelar"))
async def senha_cancel_cmd(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Operação cancelada.")


@router.message(StateFilter(SaqueFlow.aguardando_senha))
async def senha_recebida(msg: Message, state: FSMContext, bot: Bot):
    from database import checar_senha

    texto = (msg.text or "").strip()

    # Apaga a msg da senha SEMPRE
    try:
        await msg.delete()
    except Exception:
        pass

    if not texto.isdigit() or len(texto) != 6:
        await msg.answer("❌ A senha deve ter 6 dígitos numéricos.")
        return

    if not checar_senha(msg.from_user.id, texto):
        # senha errada — tenta de novo
        await msg.answer(texto_senha_errada(), parse_mode="HTML")
        return

    data = await state.get_data()
    valor = data.get("valor")
    if not valor:
        await msg.answer("❌ Sessão expirada. Refaça o processo.")
        await state.clear()
        return

    chave = get_chave_pix(msg.from_user.id) or {}
    saldo = get_saldo(msg.from_user.id)
    if valor > saldo:
        await msg.answer("❌ Saldo insuficiente.")
        await state.clear()
        return

    # EDITA status: processando
    status_msg = await msg.answer(texto_saque_processando(), parse_mode="HTML")
    await asyncio.sleep(2)

    # Cria saque + debita
    txid = uuid.uuid4().hex[:12].upper()
    chave_masc = mascarar(chave.get("tipo"), chave.get("chave"))
    saque_id = criar_saque(
        msg.from_user.id, valor,
        chave.get("tipo"), chave_masc,
        chave.get("titular_nome"), chave.get("titular_banco"),
        txid,
    )
    debitar_saldo(msg.from_user.id, valor)

    from database import get_compra  # noqa (evita linter) — não usado aqui
    # Carrega o saque criado
    with __import__("sqlite3").connect("bot.db") as _c:
        _c.row_factory = __import__("sqlite3").Row
        saque = dict(_c.execute("SELECT * FROM saques WHERE id = ?", (saque_id,)).fetchone())

    # EDITA processando → sucesso
    try:
        await status_msg.edit_text(texto_saque_ok(), parse_mode="HTML")
    except TelegramBadRequest:
        pass

    # NOVA MSG com comprovante em FOTO
    png = gerar_comprovante_png(saque)
    await msg.answer_photo(
        photo=BufferedInputFile(png, filename=f"comprovante_{txid}.png"),
        caption=f"🧾 <b>Comprovante de Saque</b>\nID: <code>{txid}</code>",
        reply_markup=kb_comprovante(saque_id),
        parse_mode="HTML",
    )

    await state.clear()


# ============================================================
# 📄 Receber por PDF
# ============================================================
@router.callback_query(F.data.startswith("comp_pdf:"))
async def comp_pdf(call: CallbackQuery):
    saque_id = int(call.data.split(":")[1])
    import sqlite3
    with sqlite3.connect("bot.db") as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM saques WHERE id = ?", (saque_id,)).fetchone()
    if not row or row["user_id"] != call.from_user.id:
        await call.answer("Comprovante não encontrado.", show_alert=True)
        return

    saque = dict(row)
    pdf = gerar_comprovante_pdf(saque)
    await call.message.answer_document(
        document=BufferedInputFile(pdf, filename=f"comprovante_{saque['txid']}.pdf"),
        caption="📄 <b>Comprovante em PDF</b>",
        parse_mode="HTML",
    )
    await call.answer()
