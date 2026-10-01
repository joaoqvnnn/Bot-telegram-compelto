# webapp/routes/senha.py
import re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import get_telegram_user
from db import (
    set_senha, get_senha_hash, get_config, set_config, get_user,
)

router = APIRouter(prefix="/api/senha", tags=["senha"])


class SalvarSenhaIn(BaseModel):
    senha: str
    email: str | None = None


def _email_key(user_id: int) -> str:
    return f"email_saque_{user_id}"


@router.post("/cadastrar")
async def cadastrar_senha(body: SalvarSenhaIn, user: dict = Depends(get_telegram_user)):
    # Valida: 4 a 6 dígitos numéricos
    if not re.fullmatch(r"\d{4,6}", (body.senha or "").strip()):
        raise HTTPException(400, "A senha deve ter de 4 a 6 dígitos numéricos")

    # Salva hash (a função set_senha já faz SHA256)
    set_senha(user["id"], body.senha.strip())

    # Salva email de recuperação (opcional)
    if body.email:
        email = body.email.strip().lower()
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$", email):
            raise HTTPException(400, "E-mail inválido")
        set_config(_email_key(user["id"]), email)

    return {"ok": True}


@router.get("/status")
async def status_senha(user: dict = Depends(get_telegram_user)):
    tem = get_senha_hash(user["id"]) is not None
    email = get_config(_email_key(user["id"]), "")
    return {
        "tem_senha": tem,
        "email": email,
        "user_id": user["id"],
    }


@router.post("/apagar")
async def apagar_senha(user: dict = Depends(get_telegram_user)):
    """Remove a senha (útil para testar)."""
    import sqlite3
    from contextlib import closing
    from db import DB_PATH
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("DELETE FROM senhas_saque WHERE user_id = ?", (user["id"],))
        conn.commit()
    return {"ok": True}
