# handlers/start.py
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from config import CANAL_OBRIGATORIO
from database import upsert_user, get_saldo
from keyboards import kb_gate, kb_menu
from texts import boas_vindas, bloqueio_canal

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

# ---------- /start ----------
@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    upsert_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name or "Usuário",
    )

    if await usuario_no_canal(bot, message.from_user.id):
        await enviar_boas_vindas(message, bot)
    else:
        await message.answer(bloqueio_canal(), reply_markup=kb_gate(), parse_mode="HTML")

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
        # Envia boas-vindas pro usuário automaticamente
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
