# webapp/routes/pix.py
from fastapi import APIRouter, Depends, HTTPException
from auth import get_telegram_user
from db import (
    get_user, get_saldo, criar_recarga, get_recarga, marcar_recarga_paga,
    get_config,
)
from mp_client import criar_pix, consultar_pagamento
from schemas import RecargaIn
import uuid

router = APIRouter(prefix="/api/pix", tags=["pix"])


@router.post("/recarga")
async def criar_pix_recarga(body: RecargaIn, user: dict = Depends(get_telegram_user)):
    minimo = float(get_config("recarga_minima", "4.00"))
    if body.valor < minimo:
        raise HTTPException(400, f"Valor mínimo R$ {minimo:.2f}")

    # Bônus (opcional)
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

    # Guarda o mp_id pra webhook (adiciona coluna se não existir)
    _garantir_coluna_mp_id()
    _set_mp_id(txid, mp["id"])

    return {
        "txid":            txid,
        "qr_code_base64":  mp["qr_code_base64"],
        "copia_cola":      mp["copia_cola"],
        "expires_at":      mp["expires_at"],
        "valor":           body.valor,
        "bonus":           bonus,
    }


@router.get("/status/{txid}")
async def status_pix(txid: str, user: dict = Depends(get_telegram_user)):
    rec = get_recarga(txid)
    if not rec or rec["user_id"] != user["id"]:
        raise HTTPException(404, "PIX não encontrado")

    # Se ainda não está pago, consulta o MP direto (fallback do webhook)
    if rec["status"] != "pago":
        mp_id = _get_mp_id(txid)
        if mp_id:
            mp = consultar_pagamento(mp_id)
            if mp and mp.get("status") == "approved":
                marcar_recarga_paga(txid)

    rec = get_recarga(txid)
    u = get_user(user["id"]) or {}
    return {
        "status":      rec["status"],
        "novo_saldo":  float(u.get("saldo", 0.0)),
    }


# ============ helpers MP id ============
import sqlite3
from contextlib import closing
from db import DB_PATH


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
