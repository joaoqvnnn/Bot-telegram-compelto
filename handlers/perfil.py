# handlers/perfil.py
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from database import get_user, get_saldo, estatisticas_usuario, listar_compras
from keyboards import kb_menu, kb_perfil, kb_historico
from texts import boas_vindas, texto_perfil, texto_historico_vazio, texto_historico_item

router = Router()


def _render_perfil(user_id: int) -> str:
    u = get_user(user_id) or {}
    saldo = u.get("saldo", 0.0)
    zap = u.get("whatsapp", "")
    stats = estatisticas_usuario(user_id)
    return texto_perfil(user_id, saldo, zap, stats)


# ============================================================
# 👤 7. MEU PERFIL
# ============================================================
@router.callback_query(F.data == "menu_perfil")
async def abrir_perfil(call: CallbackQuery):
    await _safe_edit(call.message, _render_perfil(call.from_user.id), kb_perfil())
    await call.answer()


@router.callback_query(F.data == "perfil_voltar")
async def perfil_voltar(call: CallbackQuery):
    await _safe_edit(
        call.message,
        boas_vindas(call.from_user.id, get_saldo(call.from_user.id)),
        kb_menu(),
    )
    await call.answer()


# -------- stubs (Módulos futuros) --------
@router.callback_query(F.data == "perfil_gift")
async def perfil_gift(call: CallbackQuery):
    await call.answer("🚧 Resgatar Gift Card — em breve", show_alert=False)


@router.callback_query(F.data == "perfil_alt")
async def perfil_alt(call: CallbackQuery):
    await call.answer("🚧 Alterar dados — em breve", show_alert=False)


# ============================================================
# 📜 8. HISTÓRICO DE COMPRAS
# ============================================================
@router.callback_query(F.data.startswith("perfil_hist:"))
async def historico(call: CallbackQuery):
    _, pag_s, filtro_s = call.data.split(":")
    pagina = int(pag_s)
    apenas_ativas = bool(int(filtro_s))

    compras = listar_compras(call.from_user.id, apenas_ativas=apenas_ativas)

    if not compras:
        await _safe_edit(call.message, texto_historico_vazio(), kb_historico([], 0, apenas_ativas))
        await call.answer()
        return

    if pagina < 0:
        pagina = 0
    if pagina >= len(compras):
        pagina = len(compras) - 1

    await _safe_edit(
        call.message,
        texto_historico_item(compras[pagina], pagina + 1, len(compras)),
        kb_historico(compras, pagina, apenas_ativas),
    )
    await call.answer()


@router.callback_query(F.data.startswith("hist_filtro:"))
async def hist_filtro(call: CallbackQuery):
    apenas_ativas = bool(int(call.data.split(":")[1]))
    compras = listar_compras(call.from_user.id, apenas_ativas=apenas_ativas)

    if not compras:
        await _safe_edit(call.message, texto_historico_vazio(), kb_historico([], 0, apenas_ativas))
    else:
        await _safe_edit(
            call.message,
            texto_historico_item(compras[0], 1, len(compras)),
            kb_historico(compras, 0, apenas_ativas),
        )
    await call.answer()


@router.callback_query(F.data == "hist_noop")
async def hist_noop(call: CallbackQuery):
    await call.answer()


# -------- helper --------
async def _safe_edit(msg, text, markup=None):
    try:
        await msg.edit_text(text, reply_markup=markup, parse_mode="HTML")
    except TelegramBadRequest:
        await msg.answer(text, reply_markup=markup, parse_mode="HTML")
