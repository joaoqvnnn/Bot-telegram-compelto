# webapp/routes/compra.py
from fastapi import APIRouter, Depends, HTTPException
from auth import get_telegram_user
from db import (
    get_produto, get_saldo, debitar_saldo, decrementar_estoque,
    pegar_credencial, criar_compra, get_compra, finalizar_carrinho,
)
from bot_notify import notificar_compra_webapp
from schemas import CompraSaldoIn
from config import BOT_USERNAME

router = APIRouter(prefix="/api/compra", tags=["compra"])


@router.post("/saldo")
async def comprar_com_saldo(body: CompraSaldoIn, user: dict = Depends(get_telegram_user)):
    if not body.itens:
        raise HTTPException(400, "Carrinho vazio")

    # Valida produtos + calcula total
    total = 0.0
    detalhes = []
    for it in body.itens:
        p = get_produto(it.produto_id)
        if not p:
            raise HTTPException(404, f"Produto {it.produto_id} não encontrado")
        if p["estoque"] < it.qtd:
            raise HTTPException(400, f"Estoque insuficiente: {p['nome']}")
        total += float(p["preco"]) * it.qtd
        detalhes.append((p, it.qtd))

    saldo = get_saldo(user["id"])
    if saldo < total:
        raise HTTPException(400, f"Saldo insuficiente. Faltam R$ {total - saldo:.2f}")

    # Debita + cria compras (uma por produto, ou agrega)
    debitar_saldo(user["id"], total)

    compras_ids = []
    for p, qtd in detalhes:
        cred = pegar_credencial(p["id"])
        if not cred:
            raise HTTPException(400, f"Sem credenciais em estoque para {p['nome']}")
        decrementar_estoque(p["id"], qtd)
        finalizar_carrinho(user["id"], p["id"])

        cid = criar_compra(
            user_id=user["id"],
            produto_id=p["id"],
            produto_nome=p["nome"],
            quantidade=qtd,
            valor_total=float(p["preco"]) * qtd,
            email=cred["email"],
            senha=cred["senha"],
        )
        compras_ids.append(cid)

        compra = get_compra(cid)
        await notificar_compra_webapp(user["id"], compra, BOT_USERNAME)

    u = get_user(user["id"])
    return {
        "ok": True,
        "compra_id": compras_ids[0] if compras_ids else None,
        "novo_saldo": float(u["saldo"]),
    }
