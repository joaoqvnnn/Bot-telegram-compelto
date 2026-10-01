# webapp/admin_auth.py
from datetime import datetime, timedelta

from fastapi import Header, HTTPException
from jose import jwt, JWTError

from config import JWT_SECRET, JWT_ALGO, JWT_EXP_HORAS
from db import get_config
from config import ADMIN_IDS  # ou defina aqui


def gerar_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXP_HORAS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def _senha_admin_configurada() -> str:
    return get_config("admin_senha", "troque-essa-senha")


def validar_senha(senha: str) -> bool:
    import hmac
    return hmac.compare_digest(senha, _senha_admin_configurada())


def get_admin_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    return int(payload["sub"])
