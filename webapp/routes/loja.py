# webapp/routes/loja.py
from fastapi import APIRouter, Depends
from auth import get_telegram_user
from db import (
    listar_produtos_webapp, listar_categorias, listar_depoimentos,
    listar_faq, get_config, listar_compras, get_user, buscar_produtos,
    registrar_carrinho,
)
from schemas import CarrinhoAbertoIn

router = APIRouter(prefix="/api", tags=["loja"])


@router.get("/produtos")
async def produtos():
    return listar_produtos_webapp()


@router.get("/produtos/buscar")
async def buscar(q: str):
    return buscar_produtos(q)


@router.get("/categorias")
async def categorias():
    return listar_categorias()


@router.get("/depoimentos")
async def depoimentos():
    return listar_depoimentos()


@router.get("/faq")
async def faq():
    return listar_faq()


@router.get("/config")
async def config_publica():
    return {
        "nome_loja":       get_config("nome_loja", "Minha Loja"),
        "cnpj":            get_config("cnpj", ""),
        "atendimento":     get_config("atendimento_link", ""),
        "horario":         get_config("horario", "Seg a Sex, 09h às 18h"),
        "whatsapp":        get_config("whatsapp", ""),
        "telegram_suporte": get_config("telegram_suporte", ""),
        "sobre":           get_config("sobre_bot", ""),
        "termos":          get_config("termos", ""),
        "privacidade":     get_config("privacidade", ""),
        "status_loja":     get_config("status_loja", "active"),  # active | maintenance
    }


@router.get("/historico")
async def historico(user: dict = Depends(get_telegram_user)):
    compras = listar_compras(user["id"])
    # Formata pro HTML
    return [
        {
            "id": c["id"],
            "date": c["data_compra"],
            "validity": c["data_vencimento"],
            "items": [{
                "id": c["produto_id"],
                "name": c["produto_nome"],
                "price": c["valor_total"] / max(c["quantidade"], 1),
                "qty": c["quantidade"],
                "credentials": [{"email": c["email"], "password": c["senha"]}],
                "activationLink": "",
            }],
        }
        for c in compras
    ]


@router.post("/carrinho/aberto")
async def carrinho_aberto(body: CarrinhoAbertoIn, user: dict = Depends(get_telegram_user)):
    registrar_carrinho(user["id"], body.produto_id)
    return {"ok": True}
