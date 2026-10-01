# webapp/mp_client.py
import logging
import mercadopago

from config import MP_ACCESS_TOKEN

log = logging.getLogger(__name__)
_sdk = mercadopago.SDK(MP_ACCESS_TOKEN) if MP_ACCESS_TOKEN else None


def criar_pix(valor: float, descricao: str, email_pagador: str, external_ref: str) -> dict | None:
    """
    Cria um pagamento PIX no Mercado Pago.
    Retorna dict com: id, status, qr_code_base64, copia_cola, expires_at
    """
    if not _sdk:
        log.warning("MP_ACCESS_TOKEN não configurado — usando mock")
        return _mock_pix(valor, external_ref)

    payload = {
        "transaction_amount": round(float(valor), 2),
        "description": descricao,
        "payment_method_id": "pix",
        "external_reference": external_ref,
        "payer": {"email": email_pagador or "cliente@loja.com"},
    }
    try:
        result = _sdk.payment().create(payload)
        r = result.get("response", {})
        poi = (r.get("point_of_interaction") or {}).get("transaction_data") or {}
        return {
            "id": r.get("id"),
            "status": r.get("status"),
            "qr_code_base64": poi.get("qr_code_base64"),
            "copia_cola": poi.get("qr_code"),
            "expires_at": r.get("date_of_expiration"),
        }
    except Exception as e:
        log.exception("Erro MP: %s", e)
        return None


def consultar_pagamento(mp_id: int) -> dict | None:
    if not _sdk:
        return None
    try:
        result = _sdk.payment().get(mp_id)
        return result.get("response")
    except Exception as e:
        log.exception("Erro consultando MP: %s", e)
        return None


def _mock_pix(valor: float, ref: str) -> dict:
    """Mock para dev sem token."""
    import base64
    import io
    import qrcode
    from datetime import datetime, timedelta

    code = f"00020126PIX-MOCK-{ref}-{valor:.2f}"
    img = qrcode.make(code)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()

    return {
        "id": abs(hash(ref)) % 10**9,
        "status": "pending",
        "qr_code_base64": b64,
        "copia_cola": code,
        "expires_at": (datetime.utcnow() + timedelta(minutes=30)).isoformat(),
    }
