# webapp/routes/pix.py
import uuid
import sqlite3
from contextlib import closing

from fastapi import APIRouter, Depends, HTTPException
from auth import get_telegram_user
from db import (
    get_user, get_saldo, criar_recarga, get_recarga, marcar_recarga_paga,
    get_config, DB_PATH,
)
from mp_client import criar_pix, consultar_pagamento
from schemas import RecargaIn, CompraPixIn

router = APIRouter(prefix="/api/pix", tags=["pix"])


# ---------- helpers mp_id ----------
def _garantir_coluna_mp_id():
    with closing(sqlite3.connect(DB_PATH)) as c:
        try:
            c.execute("ALTER TABLE recargas ADD COLUMN mp_id INTEGER DEFAULT 0")
            c.commit()
        except sqlite3.OperationalError:
            pass


def _set_mp_id(txid: str, mp_id: int):
    with closing(sqlite3.connect(DB_PATH)) as c:
        c.execute("UPDATE recargas SET mp_id = ? WHERE txid = ?", (mp_id, txid))
        c.commit()


def _get_mp_id(txid: str) -> int:
    with closing(sqlite3.connect(DB_PATH)) as c:
        cur = c.execute("SELECT mp_id FROM recargas WHERE txid = ?", (txid,))
        row = cur.fetchone()
        return int(row[0]) if row and row[0] else 0


# ---------- /recarga ----------
@router.post("/recarga")
async def criar_pix_recarga(body: RecargaIn, user: dict = Depends(get_telegram_user)):
    minimo = float(get_config("recarga_minima", "4.00"))
    if body.valor < minimo:
        raise HTTPException(400, f"Valor mínimo R$ {minimo:.2f}")

    bonus_ativo = get_config("recarga_bonus_ativo", "1") == "1"
    bonus_pct   = float(get_config("recarga_bonus_pct", "10"))
    bonus_min   = float(get_config("recarga_bonus_min", "10.00"))
    bonus = round(body.valor * bonus_pct / 100, 2) if (bonus_ativo and body.valor >= bonus_min) else 0.0

    txid = uuid.uuid4().hex[:16].upper()
    mp = criar_pix(
        valor=body.valor,
        descricao=f"Recarga saldo R$ {body.valor:.2f}",
        email_pagador=f"{user['id']}@loja.local",
        external_ref=txid,
    )
    if not mp:
        raise HTTPException(502, "Falha ao gerar PIX")

    criar_recarga(txid, user["id"], body.valor, bonus, mp["copia_cola"])
    _garantir_coluna_mp_id()
    _set_mp_id(txid, mp["id"])

    return {
        "txid":           txid,
        "qr_code_base64": mp["qr_code_base64"],
        "copia_cola":     mp["copia_cola"],
        "expires_at":     mp["expires_at"],
        "valor":          body.valor,
        "bonus":          bonus,
    }


# ---------- /compra (mesmo fluxo, mas vincula a compra) ----------
@router.post("/compra")
async def criar_pix_compra(body: CompraPixIn, user: dict = Depends(get_telegram_user)):
    if not body.itens:
        raise HTTPException(400, "Carrinho vazio")

    # Calcula total real (não confia no valor do front)
    from db import get_produto
    total = 0.0
    for it in body.itens:
        p = get_produto(it.produto_id)
        if not p:
            raise HTTPException(404, f"Produto {it.produto_id} não encontrado")
        total += float(p["preco"]) * it.qtd

    txid = uuid.uuid4().hex[:16].upper()
    mp = criar_pix(
        valor=total,
        descricao=f"Compra loja R$ {total:.2f}",
        email_pagador=f"{user['id']}@loja.local",
        external_ref=txid,
    )
    if not mp:
        raise HTTPException(502, "Falha ao gerar PIX")

    # Guarda os itens na recarga (reaproveita a tabela p/ rastrear)
    criar_recarga(txid, user["id"], total, 0.0, mp["copia_cola"])
    _garantir_coluna_mp_id()
    _set_mp_id(txid, mp["id"])

    return {
        "txid":           txid,
        "qr_code_base64": mp["qr_code_base64"],
        "copia_cola":     mp["copia_cola"],
        "expires_at":     mp["expires_at"],
        "valor":          total,
        "bonus":          0.0,
    }


# ---------- /status/{txid} ----------
@router.get("/status/{txid}")
async def status_pix(txid: str, user: dict = Depends(get_telegram_user)):
    rec = get_recarga(txid)
    if not rec or rec["user_id"] != user["id"]:
        raise HTTPException(404, "PIX não encontrado")

    # Fallback: se ainda não pago, consulta o MP direto
    if rec["status"] != "pago":
        mp_id = _get_mp_id(txid)
        if mp_id:
            mp = consultar_pagamento(mp_id)
            if mp and mp.get("status") == "approved":
                marcar_recarga_paga(txid)

    rec = get_recarga(txid)
    u = get_user(user["id"]) or {}
    return {
        "status":     rec["status"],
        "novo_saldo": float(u.get("saldo", 0.0)),
        "compra_id":  None,  # compra_id só faz sentido quando pago via /api/compra/saldo
    }
