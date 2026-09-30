# handlers/pesquisar.py
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery, Message, ForceReply,
    InlineQuery, InlineQueryResultPhoto, InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.exceptions import TelegramBadRequest

from database import buscar_produtos, get_produto
from keyboards import kb_pesquisar_resultado, kb_pesquisar_pedir, kb_menu
from texts import (
    texto_pesquisar_instrucoes, texto_pesquisar_forcar_reply,
    texto_pesquisar_vazio, texto_pesquisar_resultado, boas_vindas,
)
from database import get_saldo

router = Router()

PLACEHOLDER_IMG = "https://placehold.co/600x400/1f2937/ffffff?text=Servico"


class Pesquisa(StatesGroup):
    aguardando = State()


# ============================================================
# 17.1 — Botão "🔎 Pesquisar Serviços"
# ============================================================
@router.callback_query(F.data == "menu_pesquisar")
async def abrir_pesquisa(call: CallbackQuery, state: FSMContext):
    await state.set_state(Pesquisa.aguardando)

    try:
        await call.message.edit_text(
            texto_pesquisar_instrucoes(),
            reply_markup=kb_pesquisar_pedir(),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        pass

    await call.message.answer(
        texto_pesquisar_forcar_reply(),
        reply_markup=ForceReply(selective=True),
    )
    await call.answer()


@router.callback_query(F.data == "pesq_cancel")
async def pesq_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await call.message.edit_text(
            boas_vindas(call.from_user.id, get_saldo(call.from_user.id)),
            reply_markup=kb_menu(),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        pass
    await call.answer()


# ============================================================
# 17.2 — Recebe termo via ForceReply
# ============================================================
@router.message(StateFilter(Pesquisa.aguardando), Command("cancelar"))
async def pesq_cancel_cmd(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Pesquisa cancelada.")


@router.message(StateFilter(Pesquisa.aguardando))
async def pesq_receber(msg: Message, state: FSMContext):
    await state.clear()
    termo = (msg.text or "").strip()

    # Permite o usuário digitar "procurar netflix" ou só "netflix"
    if termo.lower().startswith("procurar"):
        termo = termo[8:].strip()

    if not termo:
        await msg.answer(texto_pesquisar_vazio("—"), parse_mode="HTML")
        return

    await _enviar_resultados(msg, termo)


# ============================================================
# 17.3 — Digitar "procurar <termo>" direto no chat
# ============================================================
@router.message(F.text.regexp(r"(?i)^/?procurar\s+.+"))
async def procurar_direto(msg: Message, state: FSMContext):
    # Ignora se está em outro fluxo
    if await state.get_state() is not None:
        return

    # Extrai termo
    texto = msg.text or ""
    termo = texto.split(" ", 1)[1].strip()
    if not termo:
        await msg.answer(texto_pesquisar_vazio("—"), parse_mode="HTML")
        return

    await _enviar_resultados(msg, termo)


async def _enviar_resultados(msg: Message, termo: str):
    produtos = buscar_produtos(termo)
    if not produtos:
        await msg.answer(texto_pesquisar_vazio(termo), parse_mode="HTML")
        return

    # Envia 1 por 1 com foto + caption + botão Comprar
    for p in produtos:
        img = p.get("imagem_url") or PLACEHOLDER_IMG
        try:
            await msg.answer_photo(
                photo=img,
                caption=texto_pesquisar_resultado(p),
                reply_markup=kb_pesquisar_resultado(p["id"]),
                parse_mode="HTML",
            )
        except TelegramBadRequest:
            # fallback: se a URL da imagem for inválida, envia texto
            await msg.answer(
                texto_pesquisar_resultado(p),
                reply_markup=kb_pesquisar_resultado(p["id"]),
                parse_mode="HTML",
            )


# ============================================================
# 17.4 — Inline Mode: "@seubot procurar netflix"
# ⚠️ Habilite em @BotFather → /setinline
# ============================================================
@router.inline_query()
async def inline_busca(query: InlineQuery):
    texto = (query.query or "").strip()
    if texto.lower().startswith("procurar"):
        texto = texto[8:].strip()

    if not texto:
        await query.answer([], cache_time=1, is_personal=True)
        return

    produtos = buscar_produtos(texto, limite=20)
    if not produtos:
        await query.answer([], cache_time=1, is_personal=True)
        return

    resultados = []
    for p in produtos:
        img = p.get("imagem_url") or PLACEHOLDER_IMG
        resultados.append(
            InlineQueryResultPhoto(
                id=str(p["id"]),
                photo_url=img,
                thumbnail_url=img,
                title=p["nome"],
                description=f"R$ {p['preco']:.2f}  •  Estoque: {p['estoque']}",
                caption=texto_pesquisar_resultado(p),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text="🛒 Comprar",
                        url=_deep_link(query.bot.username, p["id"]),
                    )],
                ]),
            )
        )

    await query.answer(resultados, cache_time=1, is_personal=True)


def _deep_link(bot_username: str, produto_id: int) -> str:
    """Link direto p/ o produto (deep link). O /start trata via Deep Linking."""
    return f"https://t.me/{bot_username}?start=prod_{produto_id}"
