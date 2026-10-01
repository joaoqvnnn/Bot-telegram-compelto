# webapp/routes/loja.py
from fastapi import APIRouter, Depends
from auth import get_telegram_user
from db import (
    listar_produtos_webapp, listar_categorias_webapp,
    listar_depoimentos_webapp, listar_faq_webapp, listar_promos_webapp,
    config_webapp, historico_webapp, buscar_produtos,
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
    return listar_categorias_webapp()


@router.get("/promos")
async def promos():
    return listar_promos_webapp()


@router.get("/depoimentos")
async def depoimentos():
    return listar_depoimentos_webapp()


@router.get("/faq")
async def faq():
    return listar_faq_webapp()


@router.get("/config")
async def config_publica():
    return config_webapp()


@router.get("/historico")
async def historico(user: dict = Depends(get_telegram_user)):
    return historico_webapp(user["id"])


@router.post("/carrinho/aberto")
async def carrinho_aberto(body: CarrinhoAbertoIn, user: dict = Depends(get_telegram_user)):
    registrar_carrinho(user["id"], body.produto_id)
    return {"ok": True}
