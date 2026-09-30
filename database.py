# database.py
import sqlite3
import hashlib
from contextlib import closing

DB_PATH = "bot.db"


def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        # ---- users ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                first_name  TEXT,
                saldo       REAL DEFAULT 0.0,
                whatsapp    TEXT DEFAULT '',
                criado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Migração leve p/ DBs antigos
        try:
            conn.execute("ALTER TABLE users ADD COLUMN whatsapp TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass

        # ---- produtos ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                nome          TEXT NOT NULL,
                preco         REAL NOT NULL,
                estoque       INTEGER DEFAULT 0,
                descricao     TEXT DEFAULT '',
                garantia      INTEGER DEFAULT 0,
                vendidos      INTEGER DEFAULT 0,
                vendo_agora   INTEGER DEFAULT 0
            )
        """)
        # Migração leve: campo imagem_url em produtos
        try:
            conn.execute("ALTER TABLE produtos ADD COLUMN imagem_url TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass

        # ---- pagamentos ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pagamentos (
                txid        TEXT PRIMARY KEY,
                user_id     INTEGER NOT NULL,
                produto_id  INTEGER,
                valor       REAL NOT NULL,
                status      TEXT DEFAULT 'pendente',
                copia_cola  TEXT,
                criado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expira_em   TIMESTAMP
            )
        """)

        # ---- compras (Módulo 3) ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS compras (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id          INTEGER NOT NULL,
                produto_id       INTEGER NOT NULL,
                produto_nome     TEXT    NOT NULL,
                quantidade       INTEGER DEFAULT 1,
                valor_total      REAL    NOT NULL,
                email            TEXT DEFAULT '',
                senha            TEXT DEFAULT '',
                status           TEXT DEFAULT 'ativo',
                data_compra      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_vencimento  TIMESTAMP
            )
        """)

        # ---- credenciais de estoque (Módulo 3) ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS credenciais_estoque (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id  INTEGER NOT NULL,
                email       TEXT NOT NULL,
                senha       TEXT NOT NULL,
                usado       INTEGER DEFAULT 0
            )
        """)

        # ============== MÓDULO 4 ==============

        # ---- gifts (Seção 9) ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS gifts (
                codigo       TEXT PRIMARY KEY,
                valor        REAL NOT NULL,
                produto_id   INTEGER,
                usado        INTEGER DEFAULT 0,
                usado_por    INTEGER,
                criado_em    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ---- recargas (Seção 11) ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS recargas (
                txid         TEXT PRIMARY KEY,
                user_id      INTEGER NOT NULL,
                valor        REAL NOT NULL,
                bonus        REAL DEFAULT 0.0,
                status       TEXT DEFAULT 'pendente',
                copia_cola   TEXT,
                criado_em    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expira_em    TIMESTAMP
            )
        """)

        # ---- afiliados (Seção 12) ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS afiliados (
                user_id       INTEGER PRIMARY KEY,
                ativo         INTEGER DEFAULT 0,
                comissao      REAL DEFAULT 20.0,
                indicacoes    INTEGER DEFAULT 0,
                total_ganho   REAL DEFAULT 0.0,
                criado_em     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ---- config admin ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS config_admin (
                chave  TEXT PRIMARY KEY,
                valor  TEXT
            )
        """)
        defaults = {
            "recarga_minima":          "4.00",
            "recarga_bonus_ativo":     "1",
            "recarga_bonus_pct":       "10",
            "recarga_bonus_min":       "10.00",
            "comissao_afiliado_pct":   "20.0",
            "saque_minimo_afiliado":   "20.00",
            "atendimento_link":        "",
            "atendimento_mensagem":    "Olá, vim através do bot e gostaria de ajuda.",
        }
        for k, v in defaults.items():
            conn.execute("INSERT OR IGNORE INTO config_admin (chave, valor) VALUES (?, ?)", (k, v))

        # ============== MÓDULO 5 ==============

        # ---- senha de saque (14) ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS senhas_saque (
                user_id     INTEGER PRIMARY KEY,
                senha_hash  TEXT NOT NULL,
                criado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ---- chave PIX confirmada (14.4) ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chaves_pix (
                user_id        INTEGER PRIMARY KEY,
                tipo           TEXT NOT NULL,
                chave          TEXT NOT NULL,
                titular_nome   TEXT,
                titular_banco  TEXT,
                criado_em      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ---- saques (13 / 14) ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS saques (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL,
                valor           REAL NOT NULL,
                chave_tipo      TEXT,
                chave_mascarada TEXT,
                titular_nome    TEXT,
                titular_banco   TEXT,
                status          TEXT DEFAULT 'concluido',
                txid            TEXT,
                criado_em       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ---- seed produtos ----
        cur = conn.execute("SELECT COUNT(*) FROM produtos")
        if cur.fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO produtos (nome, preco, estoque, descricao, garantia, vendidos, vendo_agora) VALUES (?,?,?,?,?,?,?)",
                [
                    ("Tela de Exemplo", 25.00, 10, "Acesso premium por 30 dias.", 7, 128, 34),
                    ("Plano VIP",       50.00, 5,  "Todos os recursos VIP.",        30, 89,  12),
                ],
            )

        # ---- seed credenciais ----
        cur = conn.execute("SELECT COUNT(*) FROM credenciais_estoque")
        if cur.fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO credenciais_estoque (produto_id, email, senha) VALUES (?,?,?)",
                [
                    (1, "cliente01@exemplo.com", "senhaABC123"),
                    (1, "cliente02@exemplo.com", "senhaDEF456"),
                    (1, "cliente03@exemplo.com", "senhaGHI789"),
                    (1, "cliente04@exemplo.com", "senhaJKL012"),
                    (1, "cliente05@exemplo.com", "senhaMNO345"),
                    (1, "cliente06@exemplo.com", "senhaPQR678"),
                    (1, "cliente07@exemplo.com", "senhaSTU901"),
                    (1, "cliente08@exemplo.com", "senhaVWX234"),
                    (1, "cliente09@exemplo.com", "senhaYZA567"),
                    (1, "cliente10@exemplo.com", "senhaBCD890"),
                    (2, "vip01@exemplo.com",     "vipAAA111"),
                    (2, "vip02@exemplo.com",     "vipBBB222"),
                    (2, "vip03@exemplo.com",     "vipCCC333"),
                    (2, "vip04@exemplo.com",     "vipDDD444"),
                    (2, "vip05@exemplo.com",     "vipEEE555"),
                ],
            )

        # ---- seed gift exemplo ----
        cur = conn.execute("SELECT COUNT(*) FROM gifts")
        if cur.fetchone()[0] == 0:
            conn.execute(
                "INSERT INTO gifts (codigo, valor, produto_id) VALUES (?, ?, ?)",
                ("ABC123XYZ456", 25.00, 1),
            )

        conn.commit()


# ---------------- users ----------------
def get_user(user_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def upsert_user(user_id: int, username: str, first_name: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("""
            INSERT INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                first_name=excluded.first_name
        """, (user_id, username, first_name))
        conn.commit()


def get_saldo(user_id: int) -> float:
    u = get_user(user_id)
    return u["saldo"] if u else 0.0


def set_whatsapp(user_id: int, numero: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("UPDATE users SET whatsapp = ? WHERE user_id = ?", (numero, user_id))
        conn.commit()


def creditar_saldo(user_id: int, valor: float):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("UPDATE users SET saldo = saldo + ? WHERE user_id = ?", (valor, user_id))
        conn.commit()


def debitar_saldo(user_id: int, valor: float):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("UPDATE users SET saldo = saldo - ? WHERE user_id = ?", (valor, user_id))
        conn.commit()


# ---------------- produtos ----------------
def listar_produtos():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM produtos ORDER BY id")
        return [dict(r) for r in cur.fetchall()]


def get_produto(pid: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM produtos WHERE id = ?", (pid,))
        row = cur.fetchone()
        return dict(row) if row else None


def decrementar_estoque(produto_id: int, qtd: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "UPDATE produtos SET estoque = estoque - ?, vendidos = vendidos + ? WHERE id = ?",
            (qtd, qtd, produto_id),
        )
        conn.commit()


# ---------------- pagamentos ----------------
def criar_pagamento(txid: str, user_id: int, produto_id: int, valor: float, copia_cola: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("""
            INSERT INTO pagamentos (txid, user_id, produto_id, valor, copia_cola, expira_em)
            VALUES (?, ?, ?, ?, ?, datetime('now', '+30 minutes'))
        """, (txid, user_id, produto_id, valor, copia_cola))
        conn.commit()


def get_pagamento(txid: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM pagamentos WHERE txid = ?", (txid,))
        row = cur.fetchone()
        return dict(row) if row else None


def marcar_pago(txid: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("UPDATE pagamentos SET status='pago' WHERE txid = ?", (txid,))
        conn.commit()


# ---------------- credenciais ----------------
def pegar_credencial(produto_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT * FROM credenciais_estoque WHERE produto_id = ? AND usado = 0 ORDER BY id LIMIT 1",
            (produto_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        conn.execute("UPDATE credenciais_estoque SET usado = 1 WHERE id = ?", (row["id"],))
        conn.commit()
        return dict(row)


# ---------------- compras ----------------
def criar_compra(user_id, produto_id, produto_nome, quantidade, valor_total, email, senha):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute("""
            INSERT INTO compras
                (user_id, produto_id, produto_nome, quantidade, valor_total, email, senha, data_vencimento)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now', '+30 days'))
        """, (user_id, produto_id, produto_nome, quantidade, valor_total, email, senha))
        conn.commit()
        return cur.lastrowid


def get_compra(compra_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM compras WHERE id = ?", (compra_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def listar_compras(user_id: int, apenas_ativas: bool = False):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        if apenas_ativas:
            cur = conn.execute(
                "SELECT * FROM compras WHERE user_id = ? AND status='ativo' ORDER BY id DESC",
                (user_id,),
            )
        else:
            cur = conn.execute(
                "SELECT * FROM compras WHERE user_id = ? ORDER BY id DESC",
                (user_id,),
            )
        return [dict(r) for r in cur.fetchall()]


def estatisticas_usuario(user_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(valor_total),0) FROM compras WHERE user_id = ?",
            (user_id,),
        )
        qtd, gasto = cur.fetchone()
        return {"qtd": qtd, "gasto": gasto or 0.0}


# ============== CONFIG ADMIN ==============
def get_config(chave: str, default: str = "") -> str:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute("SELECT valor FROM config_admin WHERE chave = ?", (chave,))
        row = cur.fetchone()
        return row[0] if row else default


def set_config(chave: str, valor: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "INSERT INTO config_admin (chave, valor) VALUES (?, ?) "
            "ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor",
            (chave, str(valor)),
        )
        conn.commit()


# ============== GIFTS ==============
def get_gift(codigo: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM gifts WHERE codigo = ?", (codigo,))
        row = cur.fetchone()
        return dict(row) if row else None


def resgatar_gift(codigo: str, user_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "UPDATE gifts SET usado = 1, usado_por = ? WHERE codigo = ?",
            (user_id, codigo),
        )
        conn.commit()


# ============== RECARGAS ==============
def criar_recarga(txid: str, user_id: int, valor: float, bonus: float, copia_cola: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("""
            INSERT INTO recargas (txid, user_id, valor, bonus, copia_cola, expira_em)
            VALUES (?, ?, ?, ?, ?, datetime('now', '+30 minutes'))
        """, (txid, user_id, valor, bonus, copia_cola))
        conn.commit()


def get_recarga(txid: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM recargas WHERE txid = ?", (txid,))
        row = cur.fetchone()
        return dict(row) if row else None


def marcar_recarga_paga(txid: str) -> bool:
    """Marca paga e credita valor + bônus. Retorna True se foi a 1ª vez."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM recargas WHERE txid = ?", (txid,))
        row = cur.fetchone()
        if not row or row["status"] == "pago":
            return False
        conn.execute("UPDATE recargas SET status='pago' WHERE txid = ?", (txid,))
        total = float(row["valor"]) + float(row["bonus"] or 0)
        conn.execute("UPDATE users SET saldo = saldo + ? WHERE user_id = ?", (total, row["user_id"]))
        conn.commit()
        return True


# ============== AFILIADOS ==============
def get_afiliado(user_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM afiliados WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def ativar_afiliado(user_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("""
            INSERT INTO afiliados (user_id, ativo) VALUES (?, 1)
            ON CONFLICT(user_id) DO UPDATE SET ativo = 1
        """, (user_id,))
        conn.commit()


# ============== MÓDULO 5 — SENHA / CHAVE / SAQUES ==============
def _hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def get_senha_hash(user_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute("SELECT senha_hash FROM senhas_saque WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return row[0] if row else None


def set_senha(user_id: int, senha: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("""
            INSERT INTO senhas_saque (user_id, senha_hash) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET senha_hash = excluded.senha_hash
        """, (user_id, _hash_senha(senha)))
        conn.commit()


def checar_senha(user_id: int, senha: str) -> bool:
    return get_senha_hash(user_id) == _hash_senha(senha)


def get_chave_pix(user_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM chaves_pix WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def set_chave_pix(user_id, tipo, chave, nome, banco):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("""
            INSERT INTO chaves_pix (user_id, tipo, chave, titular_nome, titular_banco)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                tipo=excluded.tipo, chave=excluded.chave,
                titular_nome=excluded.titular_nome, titular_banco=excluded.titular_banco
        """, (user_id, tipo, chave, nome, banco))
        conn.commit()


def criar_saque(user_id, valor, chave_tipo, chave_mascarada, titular_nome, titular_banco, txid):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute("""
            INSERT INTO saques (user_id, valor, chave_tipo, chave_mascarada, titular_nome, titular_banco, txid)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, valor, chave_tipo, chave_mascarada, titular_nome, titular_banco, txid))
        conn.commit()
        return cur.lastrowid


def listar_saques(user_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT * FROM saques WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        )
        return [dict(r) for r in cur.fetchall()]


# ============== MÓDULO 6 — BUSCA ==============
def buscar_produtos(termo: str, limite: int = 20):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        like = f"%{termo}%"
        cur = conn.execute("""
            SELECT * FROM produtos
            WHERE nome LIKE ? OR descricao LIKE ?
            ORDER BY id LIMIT ?
        """, (like, like, limite))
        return [dict(r) for r in cur.fetchall()]
