# handlers/start.py
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, ForceReply
from aiogram.exceptions import TelegramBadRequest

from config import CANAL_OBRIGATORIO, is_admin
from database import (
    upsert_user, get_saldo, get_produto, get_compra,
    listar_produtos, get_user, estatisticas_usuario,
    get_afiliado, get_config,
    registrar_conversao_campanha, registrar_indicacao,
)
from keyboards import (
    kb_gate, kb_menu, kb_produto, kb_entrega,
    kb_catalogo, kb_recarga_menu, kb_gift_pedir,
    kb_afiliado_inativo, kb_afiliado_ativo, kb_perfil,
)
from texts import (
    boas_vindas, bloqueio_canal, texto_produto, texto_entrega,
    texto_catalogo, texto_recarga_menu, texto_gift_pedir,
    texto_afiliado_inativo, texto_afiliado_ativo, texto_perfil,
)

router = Router()


# ---------- helpers ----------
async def usuario_no_canal(bot: Bot, user_id: int) -> bool:
    try:
        membro = await bot.get_chat_member(chat_id=CANAL_OBRIGATORIO, user_id=user_id)
        return membro.status in ("member", "administrator", "creator")
    except TelegramBadRequest:
        return False


async def enviar_boas_vindas(msg: Message, bot: Bot, edit: bool = False):
    uid = msg.chat.id
    saldo = get_saldo(uid)
    texto = boas_vindas(uid, saldo)

    if edit:
        try:
            await msg.edit_text(texto, reply_markup=kb_menu(), parse_mode="HTML")
            return
        except TelegramBadRequest:
            pass
    await bot.send_message(uid, texto, reply_markup=kb_menu(), parse_mode="HTML")


# ============================================================
# ROTEADOR DE PAYLOAD (deep link) — tudo cai aqui
# ============================================================
async def rotear_payload(message: Message, payload: str):
    """Recebe um payload e leva o usuário DIRETO ao fluxo certo."""
    uid = message.from_user.id

    # ---- prod_<id> → tela do produto ----
    if payload.startswith("prod_"):
        try:
            pid = int(payload[5:])
        except ValueError:
            pid = 0
        produto = get_produto(pid)
        if produto:
            await message.answer(
                texto_produto(produto, get_saldo(uid)),
                reply_markup=kb_produto(pid),
                parse_mode="HTML",
            )
            return

    # ---- cat → catálogo ----
    if payload == "cat":
        await message.answer(
            texto_catalogo(get_saldo(uid)),
            reply_markup=kb_catalogo(listar_produtos()),
            parse_mode="HTML",
        )
        return

    # ---- recarga → menu de recarga ----
    if payload == "recarga":
        await message.answer(
            texto_recarga_menu(),
            reply_markup=kb_recarga_menu(),
            parse_mode="HTML",
        )
        return

    # ---- gift → fluxo de resgatar gift card ----
    if payload == "gift":
        await message.answer(
            texto_gift_pedir(),
            reply_markup=kb_gift_pedir(),
            parse_mode="HTML",
        )
        await message.answer(
            "👇 Envie o código do gift card:",
            reply_markup=ForceReply(selective=True),
        )
        return

    # ---- afiliados → tela de afiliados ----
    if payload == "afiliados":
        me = await message.bot.get_me()
        af = get_afiliado(uid)
        comissao = float(get_config("comissao_afiliado_pct", "20.0"))
        saque_min = float(get_config("saque_minimo_afiliado", "20.00"))
        if not af or not af["ativo"]:
            texto = texto_afiliado_inativo(comissao, saque_min)
            kb = kb_afiliado_inativo()
        else:
            link = f"https://t.me/{me.username}?start=ref_{uid}"
            texto = texto_afiliado_ativo(af, link, saque_min)
            kb = kb_afiliado_ativo()
        await message.answer(texto, reply_markup=kb, parse_mode="HTML")
        return

    # ---- perfil ----
    if payload == "perfil":
        u = get_user(uid) or {}
        await message.answer(
            texto_perfil(uid, u.get("saldo", 0.0), u.get("whatsapp", ""), estatisticas_usuario(uid)),
            reply_markup=kb_perfil(),
            parse_mode="HTML",
        )
        return

    # ---- ver_<compra_id> → ver compra (dono ou admin) ----
    if payload.startswith("ver_"):
        try:
            cid = int(payload[4:])
        except ValueError:
            cid = 0
        compra = get_compra(cid)
        if not compra:
            await message.answer("❌ Compra não encontrada.")
            return
        if compra["user_id"] != uid and not is_admin(uid):
            await message.answer("🔒 Você não tem permissão para ver esta compra.")
            return
        await message.answer(
            texto_entrega(compra),
            reply_markup=kb_entrega(cid),
            parse_mode="HTML",
        )
        return

    # ---- camp_<id> → campanha (registra conversão) ----
    if payload.startswith("camp_"):
        try:
            cid = int(payload[5:])
        except ValueError:
            cid = 0
        registrar_conversao_campanha(cid, uid)
        await enviar_boas_vindas(message, message.bot)
        return

    # ---- ref_<id> → indicação ----
    if payload.startswith("ref_"):
        try:
            ref = int(payload[4:])
        except ValueError:
            ref = 0
        if ref and ref != uid:
            registrar_indicacao(ref, uid)
        await enviar_boas_vindas(message, message.bot)
        return

    # ---- fallback ----
    await enviar_boas_vindas(message, message.bot)


# ---------- /start ----------
@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    upsert_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name or "Usuário",
    )

    # ---- Gate de canal ----
    if not await usuario_no_canal(bot, message.from_user.id):
        await message.answer(bloqueio_canal(), reply_markup=kb_gate(), parse_mode="HTML")
        return

    args = (message.text or "").split(maxsplit=1)
    payload = args[1].strip() if len(args) > 1 else ""

    # Roteia o payload (ou cai no fallback de boas-vindas)
    await rotear_payload(message, payload)


# ---------- botão "Já entrei" ----------
@router.callback_query(F.data == "check_join")
async def cb_check_join(call: CallbackQuery, bot: Bot):
    if await usuario_no_canal(bot, call.from_user.id):
        await call.answer("✅ Acesso liberado!", show_alert=False)
        await enviar_boas_vindas(call.message, bot, edit=True)
    else:
        await call.answer("❌ Você ainda não entrou no canal.", show_alert=True)


# ---------- Detecção automática de entrada no canal (chat_member) ----------
@router.chat_member()
async def on_chat_member(update, bot: Bot):
    # Só reage ao canal obrigatório
    if str(update.chat.id) != str(CANAL_OBRIGATORIO) and f"@{update.chat.username}" != CANAL_OBRIGATORIO:
        return
    status = update.new_chat_member.status
    if status in ("member", "administrator", "creator"):
        user = update.new_chat_member.user
        try:
            upsert_user(user.id, user.username, user.first_name or "Usuário")
            saldo = get_saldo(user.id)
            await bot.send_message(
                user.id,
                boas_vindas(user.id, saldo),
                reply_markup=kb_menu(),
                parse_mode="HTML",
            )
        except Exception:
            pass  # usuário pode ter bloqueado o bot


# ---------- Botões do menu (stub — cada um em seu módulo futuro) ----------
@router.callback_query(F.data.startswith("menu_"))
async def cb_menu(call: CallbackQuery):
    await call.answer("🚧 Em construção (módulo futuro)", show_alert=False)
