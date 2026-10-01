# webapp/routes/__init__.py
from . import auth_routes, loja, pix, compra, webhook, admin

def register(app):
    app.include_router(auth_routes.router)
    app.include_router(loja.router)
    app.include_router(pix.router)
    app.include_router(compra.router)
    app.include_router(webhook.router)
    app.include_router(admin.router)
