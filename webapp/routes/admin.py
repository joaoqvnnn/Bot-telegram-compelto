# webapp/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException
from admin_auth import validar_senha, gerar_token, get_admin_user
from db import get_config, set_config
from schemas import AdminLoginIn

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/login")
async def login(body: AdminLoginIn):
    if not validar_senha(body.senha):
        raise HTTPException(401, "Senha incorreta")
    return {
        "token": gerar_token(0),
        "redirect": "/admin",
    }


@router.get("/config")
async def ver_config(_admin=Depends(get_admin_user)):
    from db import config_webapp
    return config_webapp()


@router.put("/config")
async def atualizar_config(dados: dict, _admin=Depends(get_admin_user)):
    for k, v in dados.items():
        set_config(k, str(v))
    return {"ok": True}
