# webapp/db.py
"""
Reutiliza TODAS as funções do bot/database.py.
Assim, loja e bot leem/escrevem o MESMO banco (bot.db).
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
BOT_DIR = BASE_DIR.parent / "bot"
sys.path.insert(0, str(BOT_DIR))

# Reexporta tudo do database do bot
from database import (  # noqa: E402,F401
    # users
    get_user, upsert_user, get_saldo, set_whatsapp,
    # produtos
    listar_produtos, get_produto, buscar_produtos,
    # pagamentos
    criar_pagamento, get_pagamento, marcar_pago,
    # credenciais
    pegar_credencial,
    # compras
    criar_compra, get_compra, listar_compras, estatisticas_usuario,
    debitar_saldo, decrementar_estoque,
    # config admin
    get_config, set_config,
    # gifts
    get_gift, resgatar_gift, creditar_saldo,
    # recargas
    criar_recarga, get_recarga, marcar_recarga_paga,
    # afiliados
    get_afiliado, ativar_afiliado,
    # carrinhos
    registrar_carrinho, finalizar_carrinho, carrinhos_abandonados, marcar_carrinho_notificado,
    # campanhas
    criar_campanha, get_campanha, campanhas_pendentes,
    marcar_campanha_enviada, registrar_conversao_campanha,
    # indicações
    registrar_indicacao,
    # pagamentos expirados
    pagamentos_expirados, marcar_pagamento_expirado,
    # senha / chave PIX / saques
    get_senha_hash, set_senha, checar_senha,
    get_chave_pix, set_chave_pix, criar_saque, listar_saques,
    # helpers
    DB_PATH as _BOT_DB_PATH,
    init_db,
)

import sqlite3
from contextlib import closing
from pathlib import Path as _P

# ==============================
# Tabelas extras do WebApp (depoimentos, FAQ, categorias, verificação de idade)
# ==============================
DB_PATH = str(_BOT_DB_PATH)


def init_webapp_tables():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        # ---- depoimentos ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS depoimentos (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                nome      TEXT NOT NULL,
                texto     TEXT NOT NULL,
                estrelas  INTEGER DEFAULT 5,
                ativo     INTEGER DEFAULT 1,
                ordem     INTEGER DEFAULT 0,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ---- faq ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS faq (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                pergunta  TEXT NOT NULL,
                resposta  TEXT NOT NULL,
                ativo     INTEGER DEFAULT 1,
                ordem     INTEGER DEFAULT 0,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ---- categorias (WebApp) ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id        TEXT PRIMARY KEY,          -- ex: 'filmes', 'iptv'
                nome      TEXT NOT NULL,
                icone     TEXT DEFAULT 'package',
                trancada  INTEGER DEFAULT 0,         -- 1 = categoria +18
                ordem     INTEGER DEFAULT 0
            )
        """)

        # ---- verificação de idade ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS verificacoes_idade (
                user_id    INTEGER PRIMARY KEY,
                aprovado   INTEGER DEFAULT 0,
                frente     BLOB,
                verso      BLOB,
                motivo     TEXT DEFAULT '',
                criado_em  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ---- seeds ----
        if conn.execute("SELECT COUNT(*) FROM categorias").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO categorias (id, nome, icone, trancada, ordem) VALUES (?,?,?,?,?)",
                [
                    ("all",           "Mais vendidos",     "fire",      0, 0),
                    ("filmes",        "Filmes e Séries",   "film",      0, 1),
                    ("futebol",       "Futebol Ao Vivo",   "ball",      0, 2),
                    ("iptv",          "IPTV Completo",     "tv",        0, 3),
                    ("produtividade", "Produtividade",     "palette",   0, 4),
                    ("musica",        "Música",            "music",     0, 5),
                    ("kids",          "Kids e Família",    "users",     0, 6),
                    ("adulto",        "Adulto +18",        "lock",      1, 7),
                ],
            )

        if conn.execute("SELECT COUNT(*) FROM depoimentos").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO depoimentos (nome, texto, estrelas, ordem) VALUES (?,?,?,?)",
                [
                    ("Carlos M.", "Comprei o IPTV Elite e a qualidade é surreal. Entrega automática e super rápida. Recomendo demais!", 5, 0),
                    ("Ana Paula S.", "Melhor preço do mercado. O suporte no chat automático me ajudou na hora do pagamento. Site muito intuitivo.", 5, 1),
                    ("Roberto F.", "Já é a terceira vez que compro. Nunca tive problemas. O PIX cai na hora e o produto é liberado na mesma hora.", 5, 2),
                ],
            )

        if conn.execute("SELECT COUNT(*) FROM faq").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO faq (pergunta, resposta, ordem) VALUES (?,?,?)",
                [
                    ("Como recebo meu produto após o pagamento?",
                     "Assim que o pagamento do PIX for confirmado pelo sistema, o bot libera automaticamente os dados de acesso (e-mail e senha) aqui mesmo na tela. É tudo automático, não precisa esperar atendente.", 0),
                    ("O pagamento via PIX é seguro?",
                     "Sim! Utilizamos a tecnologia oficial do Banco Central para gerar um QR Code único para a sua compra. O valor é transferido diretamente para a loja, sem intermediários.", 1),
                    ("Qual o prazo de garantia dos produtos?",
                     "A garantia varia de acordo com o produto, mas geralmente é de 30 a 180 dias. Você pode conferir o prazo exato na tela de detalhes de cada produto antes de comprar.", 2),
                    ("Posso pedir reembolso se não funcionar?",
                     "Sim. Se o produto apresentar algum defeito e nosso suporte não conseguir resolver, você tem até 7 dias para solicitar o reembolso, conforme o Código de Defesa do Consumidor.", 3),
                    ("Como funciona o suporte?",
                     "Nosso suporte é 100% online e automatizado. Você pode usar o chat flutuante no canto inferior direito para tirar dúvidas rápidas ou falar com um atendente humano.", 4),
                ],
            )

        conn.commit()


# ============ queries extras do WebApp ============
def listar_depoimentos():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM depoimentos WHERE ativo = 1 ORDER BY ordem, id")
        return [dict(r) for r in cur.fetchall()]


def listar_faq():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM faq WHERE ativo = 1 ORDER BY ordem, id")
        return [dict(r) for r in cur.fetchall()]


def listar_categorias():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM categorias ORDER BY ordem")
        return [dict(r) for r in cur.fetchall()]


def get_categoria(cid: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM categorias WHERE id = ?", (cid,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_verificacao_idade(user_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM verificacoes_idade WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def set_verificacao_idade(user_id: int, aprovado: bool, frente: bytes = None, verso: bytes = None, motivo: str = ""):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("""
            INSERT INTO verificacoes_idade (user_id, aprovado, frente, verso, motivo)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                aprovado = excluded.aprovado,
                frente = excluded.frente,
                verso = excluded.verso,
                motivo = excluded.motivo
        """, (user_id, 1 if aprovado else 0, frente, verso, motivo))
        conn.commit()


# ============ produtos com categoria (o HTML usa `cat`) ============
def listar_produtos_webapp():
    """
    Retorna produtos no formato que o HTML espera:
    { id, cat, name, price, oldPrice?, promo?, desc, estoque }
    """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM produtos ORDER BY id")
        rows = [dict(r) for r in cur.fetchall()]

    out = []
    for r in rows:
        # usa os campos que você já tem; se não existir categoria, cai em "filmes"
        out.append({
            "id":        r["id"],
            "cat":       r.get("categoria") or "filmes",
            "name":      r["nome"],
            "price":     float(r["preco"]),
            "oldPrice":  float(r.get("preco_antigo") or 0) or None,
            "promo":     bool(r.get("promo", 0)),
            "desc":      r.get("descricao") or "",
            "estoque":   int(r.get("estoque") or 0),
            "img":       r.get("imagem_url") or "",
        })
    return out
