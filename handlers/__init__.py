# handlers/__init__.py
from . import catalogo, start


def setup_routers(dp):
    dp.include_router(catalogo.router)
    dp.include_router(start.router)
