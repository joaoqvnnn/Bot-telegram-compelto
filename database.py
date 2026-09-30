# database.py
import sqlite3
from contextlib import closing

DB_PATH = "bot.db"


def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        # ---- users (módulo 1) ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                first_name  TEXT,
                saldo       REAL DEFAULT 0.0,
                criado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ---- produtos (módulo 2) ----
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

        # ---- pagamentos PIX (módulo 2) ----
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pagamentos (
                txid        TEXT PRIMARY KEY,
                user_id     INTEGER NOT NULL,
                produto_id  INTEGER,
                valor       REAL NOT NULL,
                status      TEXT DEFAULT 'pendente',   -- pendente | pago | cancelado
                copia_cola  TEXT,
                criado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expira_em   TIMESTAMP
            )
        """)

        # ---- seed produtos exemplo ----
        cur = conn.execute("SELECT COUNT(*) FROM produtos")
        if cur.fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO produtos (nome, preco, estoque, descricao, garantia, vendidos, vendo_agora) VALUES (?,?,?,?,?,?,?)",
                [
                    ("Tela de Exemplo", 25.00, 10, "Acesso premium por 30 dias.", 7, 128, 34),
                    ("Plano VIP",       50.00, 5,  "Todos os recursos VIP.",        30, 89,  12),
                ],
            )
        conn.commit()


# ---------- users ----------
def get_user(user_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute("SELECT user_id, username, first_name, saldo FROM users WHERE user_id = ?", (user_id,))
        return cur.fetchone()


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
    row = get_user(user_id)
    return row[3] if row else 0.0


# ---------- produtos ----------
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


# ---------- pagamentos ----------
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
