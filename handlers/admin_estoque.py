# handlers/admin_estoque.py
"""
Exemplo de como disparar notificação de estoque abastecido.
Chame `abastecer_e_notificar(bot, produto_id, qtd)` no painel admin.
"""
from aiogram import Bot

from database import get_produto
import sqlite3
from contextlib import closing
from database import DB_PATH
from utils.notificacoes import notificar_estoque


def _add_estoque(produto_id: int, qtd: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("UPDATE produtos SET estoque = estoque + ? WHERE id = ?", (qtd, produto_id))
        conn.commit()


async def abastecer_e_notificar(bot: Bot, produto_id: int, qtd: int):
    _add_estoque(produto_id, qtd)
    produto = get_produto(produto_id)
    if produto:
        await notificar_estoque(bot, produto)
