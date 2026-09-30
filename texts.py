# texts.py
from config import NOME_LOJA, CLIENTES_ATENDIDOS

def boas_vindas(user_id: int, saldo: float) -> str:
    return (
        f"📡 <b>Bem-vindo à {NOME_LOJA}!</b>\n"
        f"✨ A sua central de serviços com entrega 100% automática.\n"
        f"Pagou, recebeu. Sem filas, sem precisar falar com atendente, 24 horas por dia! ⚡\n\n"
        f"🛡 <b>Segurança e Suporte:</b>\n"
        f"Mais de {CLIENTES_ATENDIDOS} clientes já passaram por aqui.\n"
        f"Participe da nossa comunidade e veja as referências\n\n"
        f"● <b>Seus Dados:</b>\n"
        f"├ 👤 ID: <code>{user_id}</code>\n"
        f"└ 💰 Saldo Atual: <b>R$ {saldo:,.2f}</b>\n\n"
        f"👇 <b>COMO COMEÇAR:</b>\n"
        f"Clique no botão \"🛍 Comprar Produtos\" abaixo para ver nosso catálogo e escolher sua tela!"
    )

def bloqueio_canal() -> str:
    return (
        "🔒 <b>Acesso Bloqueado</b>\n\n"
        "Para utilizar o bot, é necessário entrar no nosso canal oficial.\n\n"
        "👉 Entre no canal abaixo e o acesso será liberado automaticamente."
    )
