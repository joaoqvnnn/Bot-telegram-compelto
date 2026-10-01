# webapp/routes/auth_routes.py
from fastapi import APIRouter, Depends

from auth import get_telegram_user
from db import get_user, upsert_user

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/auth")
async def autenticar(user: dict = Depends(get_telegram_user)):
    """Retorna dados do usuário logado (cria se não existir)."""
    upsert_user(
        user_id=user["id"],
        username=user.get("username") or "",
        first_name=user.get("first_name") or "Usuário",
    )
    u = get_user(user["id"]) or {}

    from db import get_config
    from config import ADMIN_IDS

    return {
        "user_id":    user["id"],
        "username":   user.get("username") or "",
        "first_name": user.get("first_name") or "Usuário",
        "saldo":      float(u.get("saldo", 0.0)),
        "is_admin":   user["id"] in ADMIN_IDS,
        "loja":       get_config("nome_loja", "Minha Loja"),
    }
