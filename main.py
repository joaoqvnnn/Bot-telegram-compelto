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
    # Registrar updates de membros (para o chat_member handler funcionar)
    dp.my_chat_member  # garante atributo carregado
    setup_routers(dp)

    # Garantir que recebemos chat_member
    from aiogram.types import Update
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(
        bot,
        allowed_updates=["message", "callback_query", "chat_member", "my_chat_member"],
    )

if __name__ == "__main__":
    asyncio.run(main())
