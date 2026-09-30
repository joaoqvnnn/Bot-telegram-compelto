# handlers/afiliados.py
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from config import NOME_LOJA
from database import get_config, get_afiliado, ativar_afiliado, get_user
from keyboards import kb_afiliado_inativo, kb_afiliado_ativo, kb_menu
from texts import texto_afiliado_inativo, texto_afiliado_ativo, boas_vindas

router = Router()


def _link(bot_username: str, user_id: int) -> str:
    return f"https://t.me/{bot_username}?start=ref_{user_id}"


# ---------- Abrir ----------
@router.callback_query(F.data == "menu_afiliados")
async def abrir_afiliados(call: CallbackQuery, bot: Bot):
    me = await bot.get_me()
    af = get_afiliado(call.from_user.id)
    comissao = float(get_config("comissao_afiliado_pct", "20.0"))
    saque_min = float(get_config("saque_minimo_afiliado", "20.00"))

    if not af or not af["ativo"]:
        texto = texto_afiliado_inativo(comissao, saque_min)
        kb = kb_afiliado_inativo()
    else:
        texto = texto_afiliado_ativo(af, _link(me.username, call.from_user.id), saque_min)
        kb = kb_afiliado_ativo()

    try:
        await call.message.edit_text(texto, reply_markup=kb, parse_mode="HTML")
    except TelegramBadRequest:
        pass
    await call.answer()


# ---------- Me Filiar ----------
@router.callback_query(F.data == "af_ativar")
async def af_ativar(call: CallbackQuery, bot: Bot):
    ativar_afiliado(call.from_user.id)
    af = get_afiliado(call.from_user.id)
    me = await bot.get_me()
    saque_min = float(get_config("saque_minimo_afiliado", "20.00"))

    try:
        await call.message.edit_text(
            texto_afiliado_ativo(af, _link(me.username, call.from_user.id), saque_min),
            reply_markup=kb_afiliado_ativo(),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        pass
    await call.answer("✅ Você agora é afiliado!")


# ---------- Voltar ----------
@router.callback_query(F.data == "af_voltar")
async def af_voltar(call: CallbackQuery):
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


# ---------- Stubs (Módulo 5: Histórico PDF / Saques / Senha Mini App) ----------
@router.callback_query(F.data == "af_hist")
async def af_hist(call: CallbackQuery):
    await call.answer("🚧 Histórico de Saque (PDF) — próximo módulo", show_alert=False)


@router.callback_query(F.data == "af_saques")
async def af_saques(call: CallbackQuery):
    await call.answer("🚧 Saques — próximo módulo", show_alert=False)


@router.callback_query(F.data == "af_senha")
async def af_senha(call: CallbackQuery):
    await call.answer("🚧 Mini App Senha — próximo módulo", show_alert=False)
