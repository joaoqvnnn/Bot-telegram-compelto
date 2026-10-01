# webapp/routes/webhook.py
import logging
from fastapi import APIRouter, Request, HTTPException

from db import get_recarga, marcar_recarga_paga
from mp_client import consultar_pagamento

log = logging.getLogger(__name__)
router = APIRouter(tags=["webhook"])


@router.post("/webhook/mercadopago")
async def mp_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(400, "JSON inválido")

    log.info("Webhook MP: %s", data)

    # MP envia {action, data:{id}, type}
    payment_id = (data.get("data") or {}).get("id")
    topic = data.get("type") or data.get("topic")

    if topic != "payment" or not payment_id:
        return {"ok": True}

    # Busca detalhes no MP
    mp = consultar_pagamento(int(payment_id))
    if not mp or mp.get("status") != "approved":
        return {"ok": True}

    ref = mp.get("external_reference")
    if not ref:
        return {"ok": True}

    rec = get_recarga(ref)
    if rec and rec["status"] != "pago":
        marcar_recarga_paga(ref)
        log.info("Recarga %s marcada como paga", ref)

    return {"ok": True}
