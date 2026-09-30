# config.py
from os import getenv

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
