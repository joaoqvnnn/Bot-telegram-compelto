# utils/pdf_extrato.py
import io
from datetime import datetime

from fpdf import FPDF


def _sanitizar_nome(s: str) -> str:
    """Remove caracteres inválidos p/ nome de arquivo."""
    s = (s or "").strip()
    return "".join(c for c in s if c.isalnum() or c in "-_") or "usuario"


def nome_arquivo_extrato(user: dict) -> str:
    base = user.get("username") or user.get("first_name") or str(user["user_id"])
    return f"extrato-{_sanitizar_nome(base)}.pdf"


class _ExtratoPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Extrato do Bot", ln=True, align="C")
        self.ln(2)


def gerar_pdf_extrato(bot_username: str, user: dict, saques: list[dict]) -> bytes:
    pdf = _ExtratoPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Cabeçalho
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, f"Bot: @{bot_username}", ln=True)
    nome = user.get("first_name") or user.get("username") or "Usuário"
    pdf.cell(0, 6, f"Usuário: {nome} (ID {user['user_id']})", ln=True)
    emitido = datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.cell(0, 6, f"Emitido em: {emitido}", ln=True)
    pdf.ln(4)

    # Cabeçalhos da tabela
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(230, 230, 230)
    larguras = [40, 30, 70, 40]
    headers = ["Data", "Valor", "Chave", "Status"]
    for w, h in zip(larguras, headers):
        pdf.cell(w, 8, h, border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 10)

    if not saques:
        pdf.cell(sum(larguras), 8, "Você não possui saques.", border=1, align="C")
    else:
        for s in saques:
            data = (s.get("criado_em") or "")[:16]
            valor = f"R$ {float(s.get('valor') or 0):.2f}"
            chave = s.get("chave_mascarada") or "-"
            status = (s.get("status") or "-").capitalize()

            pdf.cell(larguras[0], 8, str(data), border=1)
            pdf.cell(larguras[1], 8, valor,     border=1, align="R")
            pdf.cell(larguras[2], 8, str(chave)[:35], border=1)
            pdf.cell(larguras[3], 8, status,    border=1, align="C")
            pdf.ln()

    return bytes(pdf.output())
