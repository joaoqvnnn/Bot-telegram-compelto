# keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton
from config import LINK_CANAL


# ---------- Módulo 1 ----------
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


# ---------- Módulo 2 ----------
def kb_catalogo(produtos: list[dict]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=f"📦 {p['nome']} — R$ {p['preco']:.2f}",
            callback_data=f"prod:{p['id']}",
        )]
        for p in produtos
    ]
    rows.append([InlineKeyboardButton(text="⬅️ VOLTAR", callback_data="cat_voltar_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_produto(pid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 COMPRAR", callback_data=f"prod_buy:{pid}")],
        [InlineKeyboardButton(text="🛒 Comprar mais de um", callback_data=f"prod_buy_multi:{pid}")],
        [InlineKeyboardButton(text="⬅️ VOLTAR", callback_data="prod_voltar_catalogo")],
    ])


def kb_saldo_insuficiente(pid: int, valor: float) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"💠 Gerar PIX de R$ {valor:.2f}",
            callback_data=f"pix_gen:{pid}:{valor}",
        )],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data=f"pix_cancel:{pid}")],
    ])


def kb_qr_pix(txid: str, copia_cola: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        # 📋 Copiar PIX — copia em silêncio (Bot API 7.11+)
        [InlineKeyboardButton(
            text="📋 Copiar PIX",
            copy_text=CopyTextButton(text=copia_cola),
        )],
        [InlineKeyboardButton(text="⏰ AGUARDANDO PAGAMENTO", callback_data=f"pix_wait:{txid}")],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data=f"pix_cancel:{txid}")],
    ])


# ---------- Módulo 3 — 5B ----------
def kb_resultado_pedido(produto_id: int, qtd: int, total: float) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✅ Confirmar Compra",
            callback_data=f"multi_conf:{produto_id}:{qtd}:{total:.2f}",
        )],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data="multi_cancel")],
    ])


def kb_saldo_insuficiente_multi(total: float) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"💠 Gerar PIX de R$ {total:.2f}",
            callback_data=f"multi_pix:{total:.2f}",
        )],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data="multi_cancel")],
    ])


# ---------- Módulo 3 — Entrega ----------
def kb_entrega(compra_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔓 VER PRODUTO", callback_data=f"ent_revelar:{compra_id}")],
        [InlineKeyboardButton(text="🔗 CLIQUE AQUI PARA ATIVAR", callback_data=f"ent_ativar:{compra_id}")],
    ])


# ---------- Módulo 3 — Perfil ----------
def kb_perfil() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📜 Histórico de Compras", callback_data="perfil_hist:0:0")],
        [InlineKeyboardButton(text="🎁 Resgatar Gift Card", callback_data="perfil_gift")],
        [InlineKeyboardButton(text="✏️ Alterar dados", callback_data="perfil_alt")],
        [InlineKeyboardButton(text="⬅️ VOLTAR", callback_data="perfil_voltar")],
    ])


# ---------- Módulo 3 — Histórico ----------
def kb_historico(compras: list, pagina: int, apenas_ativas: bool) -> InlineKeyboardMarkup:
    rows = []
    if compras:
        compra = compras[pagina]
        rows.append([InlineKeyboardButton(
            text="🔗 CLIQUE AQUI PARA ATIVAR",
            callback_data=f"ent_ativar:{compra['id']}",
        )])
        nav = []
        if pagina > 0:
            nav.append(InlineKeyboardButton(
                text="⏪ Anterior",
                callback_data=f"perfil_hist:{pagina-1}:{1 if apenas_ativas else 0}",
            ))
        nav.append(InlineKeyboardButton(
            text=f"📄 {pagina+1}/{len(compras)}",
            callback_data="hist_noop",
        ))
        if pagina < len(compras) - 1:
            nav.append(InlineKeyboardButton(
                text="⏩ Avançar >>",
                callback_data=f"perfil_hist:{pagina+1}:{1 if apenas_ativas else 0}",
            ))
        if nav:
            rows.append(nav)

    filtro_label = "🟢 Apenas Ativas" if not apenas_ativas else "🟢 Todas"
    rows.append([InlineKeyboardButton(
        text=filtro_label,
        callback_data=f"hist_filtro:{0 if apenas_ativas else 1}",
    )])
    rows.append([InlineKeyboardButton(text="⬅️ VOLTAR", callback_data="perfil_voltar")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
