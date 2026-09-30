# keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import LINK_CANAL

def kb_gate() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ ENTRAR NO CANAL", url=LINK_CANAL)],
        [InlineKeyboardButton(text="✅ Já entrei", callback_data="check_join")],
    ])

def kb_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Comprar Produtos", callback_data="menu_catalogo"),
         InlineKeyboardButton(text="🛒 Abrir Loja", url="https://t.me")],  # troque pela sua WebApp
        [InlineKeyboardButton(text="👤 Meu Perfil", callback_data="menu_perfil"),
         InlineKeyboardButton(text="💠 Recarregar Saldo", callback_data="menu_recarga")],
        [InlineKeyboardButton(text="👥 Afiliados", callback_data="menu_afiliados"),
         InlineKeyboardButton(text="🏆 Top Compradores", callback_data="menu_top")],
        [InlineKeyboardButton(text="📩 Atendimento", callback_data="menu_atendimento"),
         InlineKeyboardButton(text="🤖 Sobre o Bot", callback_data="menu_sobre")],
        [InlineKeyboardButton(text="🔎 Pesquisar Serviços", callback_data="menu_pesquisar")],
    ])
