# config.py
from os import getenv
import os as _os

BOT_TOKEN = getenv("BOT_TOKEN", "SEU_TOKEN_AQUI")

# Canal obrigatório (use @username ou ID numérico tipo -1001234567890)
CANAL_OBRIGATORIO = getenv("CANAL_OBRIGATORIO", "@seu_canal")

# Nome da loja (aparece nas boas-vindas)
NOME_LOJA = "Minha Loja"
CLIENTES_ATENDIDOS = "10.000"

# Link do canal para o botão
LINK_CANAL = f"https://t.me/{CANAL_OBRIGATORIO.lstrip('@')}"

# Nome do titular que aparece no comprovante PIX
NOME_TITULAR_CONTA = "MINHA LOJA DIGITAL"

# Lista de IDs de administradores (aceita string "123456,789012")
ADMIN_IDS = [
    int(x) for x in _os.getenv("ADMIN_IDS", "").replace(" ", "").split(",")
    if x.strip().lstrip("-").isdigit()
]


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS
