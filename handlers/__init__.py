# handlers/__init__.py
from . import entrega, compra_multi, perfil, catalogo, start


def setup_routers(dp):
    dp.include_router(entrega.router)
    dp.include_router(compra_multi.router)
    dp.include_router(perfil.router)
    dp.include_router(catalogo.router)
    dp.include_router(start.router)
