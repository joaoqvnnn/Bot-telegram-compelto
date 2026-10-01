# webapp/db.py
import sys
import sqlite3
from contextlib import closing
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
BOT_DIR = BASE_DIR.parent / "bot"
sys.path.insert(0, str(BOT_DIR))

from database import (  # noqa: E402,F401
    get_user, upsert_user, get_saldo, set_whatsapp,
    listar_produtos, get_produto, buscar_produtos,
    criar_pagamento, get_pagamento, marcar_pago,
    pegar_credencial,
    criar_compra, get_compra, listar_compras, estatisticas_usuario,
    debitar_saldo, decrementar_estoque,
    get_config, set_config,
    get_gift, resgatar_gift, creditar_saldo,
    criar_recarga, get_recarga, marcar_recarga_paga,
    get_afiliado, ativar_afiliado,
    registrar_carrinho, finalizar_carrinho, carrinhos_abandonados, marcar_carrinho_notificado,
    criar_campanha, get_campanha, campanhas_pendentes,
    marcar_campanha_enviada, registrar_conversao_campanha,
    registrar_indicacao,
    pagamentos_expirados, marcar_pagamento_expirado,
    get_senha_hash, set_senha, checar_senha,
    get_chave_pix, set_chave_pix, criar_saque, listar_saques,
    DB_PATH as _BOT_DB_PATH,
    init_db,
)

DB_PATH = str(_BOT_DB_PATH)


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


# ============================================================
# Migração — adiciona colunas que o WebApp precisa em produtos
# ============================================================
def migrar_produtos():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cols = [
            ("categoria",    "TEXT DEFAULT 'filmes'"),
            ("preco_antigo", "REAL DEFAULT 0"),
            ("promo",        "INTEGER DEFAULT 0"),
            ("imagem_url",   "TEXT DEFAULT ''"),
        ]
        for col, tipo in cols:
            try:
                conn.execute(f"ALTER TABLE produtos ADD COLUMN {col} {tipo}")
            except sqlite3.OperationalError:
                pass
        conn.commit()


# ============================================================
# Tabelas extras do WebApp
# ============================================================
def init_webapp_tables():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        # ---- depoimentos ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS depoimentos (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                author    TEXT NOT NULL,
                text      TEXT NOT NULL,
                rating    INTEGER DEFAULT 5,
                ativo     INTEGER DEFAULT 1,
                ordem     INTEGER DEFAULT 0
            )
        """)

        # ---- faq ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS faq (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                q         TEXT NOT NULL,
                a         TEXT NOT NULL,
                ativo     INTEGER DEFAULT 1,
                ordem     INTEGER DEFAULT 0
            )
        """)

        # ---- categorias ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id        TEXT PRIMARY KEY,
                name      TEXT NOT NULL,
                icon      TEXT DEFAULT 'package',
                locked    INTEGER DEFAULT 0,
                ordem     INTEGER DEFAULT 0
            )
        """)

        # ---- promos (carrossel) ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS promos (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                title             TEXT NOT NULL,
                desc              TEXT DEFAULT '',
                price             TEXT NOT NULL,
                targetProductId   INTEGER NOT NULL,
                ativo             INTEGER DEFAULT 1,
                ordem             INTEGER DEFAULT 0
            )
        """)

        # ---- verificações de idade ----
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
                "INSERT INTO categorias (id, name, icon, locked, ordem) VALUES (?,?,?,?,?)",
                [
                    ("all",           "Mais vendidos",   "fire",    0, 0),
                    ("filmes",        "Filmes e Séries", "film",    0, 1),
                    ("futebol",       "Futebol Ao Vivo", "ball",    0, 2),
                    ("iptv",          "IPTV Completo",   "tv",      0, 3),
                    ("produtividade", "Produtividade",   "palette", 0, 4),
                    ("musica",        "Música",          "music",   0, 5),
                    ("kids",          "Kids e Família",  "users",   0, 6),
                    ("adulto",        "Adulto +18",      "lock",    1, 7),
                ],
            )

        if conn.execute("SELECT COUNT(*) FROM depoimentos").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO depoimentos (author, text, rating, ordem) VALUES (?,?,?,?)",
                [
                    ("Carlos M.",    "Comprei o IPTV Elite e a qualidade é surreal. Entrega automática e super rápida. Recomendo demais!", 5, 0),
                    ("Ana Paula S.", "Melhor preço do mercado. O suporte no chat automático me ajudou na hora do pagamento. Site muito intuitivo.", 5, 1),
                    ("Roberto F.",   "Já é a terceira vez que compro. Nunca tive problemas. O PIX cai na hora e o produto é liberado na mesma hora.", 5, 2),
                ],
            )

        if conn.execute("SELECT COUNT(*) FROM faq").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO faq (q, a, ordem) VALUES (?,?,?)",
                [
                    ("Como recebo meu produto após o pagamento?",
                     "Assim que o pagamento do PIX for confirmado pelo sistema, o bot libera automaticamente os dados de acesso (e-mail e senha) aqui mesmo na tela.", 0),
                    ("O pagamento via PIX é seguro?",
                     "Sim! Utilizamos a tecnologia oficial do Banco Central para gerar um QR Code único para a sua compra. O valor é transferido diretamente para a loja.", 1),
                    ("Qual o prazo de garantia dos produtos?",
                     "A garantia varia de acordo com o produto, mas geralmente é de 30 a 180 dias.", 2),
                    ("Posso pedir reembolso se não funcionar?",
                     "Sim. Se o produto apresentar algum defeito e nosso suporte não conseguir resolver, você tem até 7 dias para solicitar o reembolso.", 3),
                    ("Como funciona o suporte?",
                     "Nosso suporte é 100% online e automatizado. Você pode usar o chat flutuante no canto inferior direito.", 4),
                ],
            )

        if conn.execute("SELECT COUNT(*) FROM promos").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO promos (title, desc, price, targetProductId, ordem) VALUES (?,?,?,?,?)",
                [
                    ("Netflix 4K",         "Qualidade máxima para a família.",           "14,90", 1, 0),
                    ("IPTV Elite 90 dias", "3 meses de estabilidade premium.",           "59,90", 2, 1),
                    ("Canva Pro 6 meses",  "Design profissional por metade do preço.",   "18,00", 1, 2),
                ],
            )

        # ---- defaults de config (Admin pode alterar depois) ----
        defaults = {
            "nome_loja":              "Joãozinho Store",
            "cnpj":                   "00.000.000/0000-00",
            "horario":                "Segunda a Sexta, 09h às 18h",
            "whatsapp":               "",
            "telegram":               "",
            "atendimento_link":       "",
            "sobre_bot":              "",
            "termos":                 "Ao comprar, você concorda com nossos termos.",
            "privacidade":            "Seus dados estão seguros e não compartilhamos com terceiros.",
            "status_loja":            "active",
            "admin_senha":            "troque-essa-senha",
            # textos dinâmicos da loja
            "balanceLabel":           "Saldo disponível",
            "addBalanceText":         "Adicionar saldo",
            "searchPlaceholder":      "O que você procura hoje?",
            "sectionTitleProducts":   "Nossos produtos",
            "sectionTitleTestimonials":"O que dizem nossos clientes",
            "sectionTitleFaq":        "Perguntas Frequentes",
            "cartButtonText":         "Ver Carrinho",
            "addToCartText":          "Adicionar ao Carrinho",
            "checkoutText":           "Usar Saldo da Carteira",
            "pixText":                "Pagar com PIX",
            "copyrightText":          "© 2026 Todos os direitos reservados.",
            "adminLinkText":          "Acesso Administrador",
            "promoBadgeText":         "PROMOÇÃO DO DIA",
            "promoButtonText":        "Aproveitar agora",
            "termsText":              "Termos de Uso",
            "privacyText":            "Privacidade",
        }
        for k, v in defaults.items():
            conn.execute(
                "INSERT OR IGNORE INTO config_admin (chave, valor) VALUES (?, ?)",
                (k, v),
            )

        conn.commit()


# ============================================================
# Formatters para o HTML
# ============================================================
def listar_produtos_webapp():
    """Formato que o HTML espera: {id, cat, name, price, oldPrice, promo, desc, estoque}"""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM produtos ORDER BY id")
        rows = [dict(r) for r in cur.fetchall()]

    out = []
    for r in rows:
        out.append({
            "id":       r["id"],
            "cat":      r.get("categoria") or "filmes",
            "name":     r["nome"],
            "price":    float(r["preco"]),
            "oldPrice": float(r.get("preco_antigo") or 0) or None,
            "promo":    bool(r.get("promo", 0)),
            "desc":     r.get("descricao") or "",
            "estoque":  int(r.get("estoque") or 0),
            "img":      r.get("imagem_url") or "",
        })
    return out


def listar_categorias_webapp():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM categorias ORDER BY ordem")
        return [
            {"id": r["id"], "name": r["name"], "icon": r["icon"], "locked": bool(r["locked"])}
            for r in cur.fetchall()
        ]


def listar_depoimentos_webapp():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM depoimentos WHERE ativo=1 ORDER BY ordem, id")
        return [
            {"author": r["author"], "text": r["text"], "rating": r["rating"]}
            for r in cur.fetchall()
        ]


def listar_faq_webapp():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM faq WHERE ativo=1 ORDER BY ordem, id")
        return [{"q": r["q"], "a": r["a"]} for r in cur.fetchall()]


def listar_promos_webapp():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM promos WHERE ativo=1 ORDER BY ordem, id")
        return [
            {
                "title": r["title"],
                "desc": r["desc"],
                "price": r["price"],
                "targetProductId": r["targetProductId"],
            }
            for r in cur.fetchall()
        ]


def config_webapp():
    """Todos os campos que o HTML espera."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT chave, valor FROM config_admin")
        cfg = {r["chave"]: r["valor"] for r in cur.fetchall()}

    return {
        # loja
        "storeName":            cfg.get("nome_loja", "Minha Loja"),
        "nome_loja":            cfg.get("nome_loja", "Minha Loja"),
        "cnpj":                 cfg.get("cnpj", ""),
        "hours":                cfg.get("horario", ""),
        "horario":              cfg.get("horario", ""),
        "whatsapp":             cfg.get("whatsapp", ""),
        "telegram":             cfg.get("telegram", ""),
        "atendimento":          cfg.get("atendimento_link", ""),
        "status":               cfg.get("status_loja", "active"),
        # textos dinâmicos
        "balanceLabel":         cfg.get("balanceLabel", "Saldo disponível"),
        "addBalanceText":       cfg.get("addBalanceText", "Adicionar saldo"),
        "searchPlaceholder":    cfg.get("searchPlaceholder", ""),
        "sectionTitleProducts": cfg.get("sectionTitleProducts", ""),
        "sectionTitleTestimonials": cfg.get("sectionTitleTestimonials", ""),
        "sectionTitleFaq":      cfg.get("sectionTitleFaq", ""),
        "cartButtonText":       cfg.get("cartButtonText", ""),
        "addToCartText":        cfg.get("addToCartText", ""),
        "checkoutText":         cfg.get("checkoutText", ""),
        "pixText":              cfg.get("pixText", ""),
        "copyrightText":        cfg.get("copyrightText", ""),
        "adminLinkText":        cfg.get("adminLinkText", ""),
        "promoBadgeText":       cfg.get("promoBadgeText", ""),
        "promoButtonText":      cfg.get("promoButtonText", ""),
        "termsText":            cfg.get("termsText", "Termos de Uso"),
        "privacyText":          cfg.get("privacyText", "Privacidade"),
        # conteúdos
        "termsContent":         cfg.get("termos", ""),
        "privacyContent":       cfg.get("privacidade", ""),
        "sobre":                cfg.get("sobre_bot", ""),
    }


def get_verificacao_idade(user_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM verificacoes_idade WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def set_verificacao_idade(user_id: int, aprovado: bool, frente: bytes, verso: bytes, motivo=""):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("""
            INSERT INTO verificacoes_idade (user_id, aprovado, frente, verso, motivo)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                aprovado=excluded.aprovado,
                frente=excluded.frente,
                verso=excluded.verso,
                motivo=excluded.motivo
        """, (user_id, 1 if aprovado else 0, frente, verso, motivo))
        conn.commit()


def historico_webapp(user_id: int):
    """Formato que o HTML espera."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT * FROM compras WHERE user_id=? ORDER BY id DESC", (user_id,)
        )
        rows = [dict(r) for r in cur.fetchall()]

    out = []
    for r in rows:
        preco_unit = float(r["valor_total"]) / max(r["quantidade"], 1)
        out.append({
            "id":       r["id"],
            "date":     (r.get("data_compra") or "")[:16],
            "validity": (r.get("data_vencimento") or "")[:10],
            "total":    float(r["valor_total"]),
            "items": [{
                "id":    r["produto_id"],
                "name":  r["produto_nome"],
                "price": preco_unit,
                "qty":   r["quantidade"],
                "credentials": [{"email": r["email"], "password": r["senha"]}],
                "activationLink": "",
            }],
        })
    return out
