# handlers/historico_saque.py
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, BufferedInputFile

from database import get_user, listar_saques
from utils.pdf_extrato import gerar_pdf_extrato, nome_arquivo_extrato

router = Router()


@router.callback_query(F.data == "af_hist")
async def historico_saque(call: CallbackQuery, bot: Bot):
    user = get_user(call.from_user.id)
    if not user:
        await call.answer("Usuário não encontrado.", show_alert=True)
        return

    saques = listar_saques(call.from_user.id)

    me = await bot.get_me()
    pdf_bytes = gerar_pdf_extrato(me.username or "bot", user, saques)
    nome_arq = nome_arquivo_extrato(user)

    await call.message.answer_document(
        document=BufferedInputFile(pdf_bytes, filename=nome_arq),
        caption="📄 <b>Extrato de Saques</b>",
        parse_mode="HTML",
    )
    await call.answer()
