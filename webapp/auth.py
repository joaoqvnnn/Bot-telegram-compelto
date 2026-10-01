# webapp/auth.py
import hmac
import hashlib
import time
from urllib.parse import parse_qsl
from typing import Optional

from fastapi import Header, HTTPException, Depends

from config import BOT_TOKEN


def validar_init_data(init_data: str) -> Optional[dict]:
    """
    Valida a assinatura do initData do Telegram WebApp.
    Retorna dict com os dados OU None se inválido.
    """
    if not init_data:
        return None

    parsed = dict(parse_qsl(init_data, strict_parsing=True))
    hash_recebido = parsed.pop("hash", None)
    if not hash_recebido:
        return None

    # auth_date expirado? (opcional — deixa 24h de validade)
    auth_date = parsed.get("auth_date")
    if auth_date:
        try:
            if time.time() - int(auth_date) > 86400:
                return None
        except ValueError:
            return None

    data_check = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    calc_hash = hmac.new(secret_key, data_check.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calc_hash, hash_recebido):
        return None

    return parsed


def get_telegram_user(x_telegram_init_data: str = Header(None, alias="X-Telegram-Init-Data")) -> dict:
    """Dependency FastAPI: injeta o user validado ou lança 401."""
    data = validar_init_data(x_telegram_init_data or "")
    if not data:
        raise HTTPException(status_code=401, detail="initData inválido")

    import json
    try:
        user = json.loads(data["user"])
    except (KeyError, json.JSONDecodeError):
        raise HTTPException(status_code=401, detail="user ausente no initData")

    return user  # {id, first_name, username, ...}
