# webapp/config.py
import os
from pathlib import Path

# ==============================
# Caminhos
# ==============================
BASE_DIR = Path(__file__).resolve().parent
BOT_DIR  = BASE_DIR.parent / "bot"
DB_PATH  = BOT_DIR / "bot.db"
INDEX_HTML = BASE_DIR / "index.html"

# ==============================
# Telegram
# ==============================
BOT_TOKEN = os.getenv("BOT_TOKEN", "")                    # mesmo do bot
BOT_USERNAME = os.getenv("BOT_USERNAME", "")              # ex: joaozinhobot

# ==============================
# Mercado Pago
# ==============================
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN", "")
MP_PUBLIC_KEY   = os.getenv("MP_PUBLIC_KEY", "")
MP_WEBHOOK_URL  = os.getenv("MP_WEBHOOK_URL", "")         # https://seu-dominio/webhook/mercadopago

# ==============================
# Segurança
# ==============================
JWT_SECRET = os.getenv("JWT_SECRET", "troque-essa-chave-super-secreta")
JWT_ALGO   = "HS256"
JWT_EXP_HORAS = 12

# ==============================
# CORS (ajuste em produção)
# ==============================
ALLOWED_ORIGINS = ["*"]   # em produção, coloque seu domínio
