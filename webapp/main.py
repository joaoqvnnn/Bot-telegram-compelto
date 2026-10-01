# webapp/main.py
import asyncio
import logging
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

from config import ALLOWED_ORIGINS, INDEX_HTML
from db import init_db, init_webapp_tables, migrar_produtos
from routes import register

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("webapp")

app = FastAPI(title="Loja WebApp", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# BOT em background (roda junto com o FastAPI)
# ============================================================
_bot_task = None


async def iniciar_bot():
    """Importa e roda o bot aiogram no mesmo loop do FastAPI."""
    BOT_DIR = Path(__file__).resolve().parent.parent / "bot"
    sys.path.insert(0, str(BOT_DIR))

    try:
        from aiogram import Bot, Dispatcher
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode
        from aiogram.types import BotCommand

        from config import BOT_TOKEN as BOT_TOKEN_LOCAL
        from database import init_db as init_bot_db
        from handlers import setup_routers
        from utils.rastreador import loop_rastreador

        init_bot_db()

        bot = Bot(
            token=BOT_TOKEN_LOCAL,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        await bot.set_my_commands([BotCommand(command="start", description="Iniciar bot")])

        dp = Dispatcher()
        setup_routers(dp)
        await bot.delete_webhook(drop_pending_updates=True)

        asyncio.create_task(loop_rastreador(bot))

        log.info("🤖 Bot iniciado em background")
        await dp.start_polling(
            bot,
            allowed_updates=["message", "callback_query", "chat_member", "my_chat_member", "inline_query"],
        )
    except Exception as e:
        log.exception("Erro no bot: %s", e)


@app.on_event("startup")
async def startup():
    global _bot_task
    init_db()
    init_webapp_tables()
    migrar_produtos()
    log.info("Banco inicializado")

    # Sobe o bot em background
    _bot_task = asyncio.create_task(iniciar_bot())


@app.on_event("shutdown")
async def shutdown():
    global _bot_task
    if _bot_task:
        _bot_task.cancel()


@app.get("/", response_class=HTMLResponse)
async def raiz():
    if not INDEX_HTML.exists():
        return HTMLResponse("<h1>index.html não encontrado</h1>", status_code=404)
    return FileResponse(INDEX_HTML, media_type="text/html")


register(app)


@app.get("/health")
async def health():
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
