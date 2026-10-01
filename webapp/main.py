# webapp/main.py
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

from config import ALLOWED_ORIGINS, INDEX_HTML
from db import init_db, init_webapp_tables, migrar_produtos
from routes import register

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("webapp")

app = FastAPI(title="Loja WebApp", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()
    init_webapp_tables()
    migrar_produtos()   # adiciona categoria/preco_antigo/promo/imagem_url em produtos
    log.info("Banco inicializado")


@app.get("/", response_class=HTMLResponse)
async def raiz():
    if not INDEX_HTML.exists():
        return HTMLResponse("<h1>index.html não encontrado</h1>", status_code=404)
    return FileResponse(INDEX_HTML, media_type="text/html")


register(app)


@app.get("/health")
async def health():
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
