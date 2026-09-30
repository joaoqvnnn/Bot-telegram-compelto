# handlers/atendimento.py
from urllib.parse import quote

from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import get_config
from keyboards import kb_atendimento
from texts import texto_atendimento_sem_config

router = Router()


@router.callback_query(F.data == "menu_atendimento")
async def abrir_atendimento(call: CallbackQuery):
    link = (get_config("atendimento_link", "") or "").strip()
    mensagem = get_config(
        "atendimento_mensagem",
        "Olá, vim através do bot e gostaria de ajuda.",
    )

    if not link:
        # Sem link configurado → edita a mensagem atual
        try:
            await call.message.edit_text(
                texto_atendimento_sem_config(),
                reply_markup=None,
                parse_mode="HTML",
            )
        except Exception:
            pass
        await call.answer()
        return

    # Monta URL com mensagem pré-preenchida
    sep = "&" if "?" in link else "?"
    url = f"{link}{sep}text={quote(mensagem)}"

    # Sempre envia NOVA MSG (link externo — não dá pra editar botão url em alguns casos)
    await call.message.answer(
        "📩 <b>Atendimento</b>\n\n"
        "Clique no botão abaixo para falar com nossa equipe:",
        reply_markup=kb_atendimento(url),
        parse_mode="HTML",
    )
    await call.answer()
