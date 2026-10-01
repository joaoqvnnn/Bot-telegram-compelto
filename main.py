# main.py
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import BOT_TOKEN
from database import init_db
from handlers import setup_routers
from utils.rastreador import loop_rastreador   # ← rastreador de carrinho/PIX

logging.basicConfig(level=logging.INFO)


async def main():
    init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # ⚠️ Essencial para detectar entrada no canal (chat_member)
    await bot.set_my_commands([BotCommand(command="start", description="Iniciar bot")])

    dp = Dispatcher()
    setup_routers(dp)

    # Garantir que recebemos chat_member
    await bot.delete_webhook(drop_pending_updates=True)

    # 🔎 inicia o rastreador em background (carrinho abandonado, PIX expirado, campanhas)
    asyncio.create_task(loop_rastreador(bot))

    await dp.start_polling(
        bot,
        allowed_updates=[
            "message", "callback_query",
            "chat_member", "my_chat_member",
            "inline_query",
        ],
    )


if __name__ == "__main__":
    asyncio.run(main())
