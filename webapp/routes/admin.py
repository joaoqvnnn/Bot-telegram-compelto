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
    return {"token": gerar_token(0)}


@router.get("/config")
async def ver_config(_admin=Depends(get_admin_user)):
    return {
        "nome_loja":       get_config("nome_loja", "Minha Loja"),
        "cnpj":            get_config("cnpj", ""),
        "whatsapp":        get_config("whatsapp", ""),
        "telegram_suporte": get_config("telegram_suporte", ""),
        "atendimento_link": get_config("atendimento_link", ""),
        "sobre_bot":       get_config("sobre_bot", ""),
        "termos":          get_config("termos", ""),
        "privacidade":     get_config("privacidade", ""),
        "status_loja":     get_config("status_loja", "active"),
        "recarga_minima":  get_config("recarga_minima", "4.00"),
        "recarga_bonus_ativo": get_config("recarga_bonus_ativo", "1"),
        "recarga_bonus_pct":   get_config("recarga_bonus_pct", "10"),
        "recarga_bonus_min":   get_config("recarga_bonus_min", "10.00"),
        "carrinho_minutos":    get_config("carrinho_minutos", "20"),
    }


@router.put("/config")
async def atualizar_config(dados: dict, _admin=Depends(get_admin_user)):
    for k, v in dados.items():
        set_config(k, str(v))
    return {"ok": True}
