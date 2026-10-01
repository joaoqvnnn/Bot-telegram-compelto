# handlers/__init__.py
from . import (
    entrega,
    compra_multi,
    gift,
    alterar_dados,
    recarga,
    senha_saque,
    saques,
    historico_saque,
    afiliados,
    atendimento,
    pesquisar,
    perfil,
    catalogo,
    start,
)


def setup_routers(dp):
    dp.include_router(entrega.router)
    dp.include_router(compra_multi.router)
    dp.include_router(gift.router)
    dp.include_router(alterar_dados.router)
    dp.include_router(recarga.router)
    dp.include_router(senha_saque.router)
    dp.include_router(saques.router)
    dp.include_router(historico_saque.router)
    dp.include_router(afiliados.router)
    dp.include_router(atendimento.router)
    dp.include_router(pesquisar.router)   # ← ANTES de catalogo (regex "procurar")
    dp.include_router(perfil.router)
    dp.include_router(catalogo.router)
    dp.include_router(start.router)
