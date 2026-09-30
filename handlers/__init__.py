# handlers/__init__.py
from . import start

def setup_routers(dp):
    dp.include_router(start.router)
