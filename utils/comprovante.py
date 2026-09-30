# utils/comprovante.py
import io
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from config import NOME_TITULAR_CONTA


def _fonte(tamanho: int, negrito: bool = False):
    try:
        nome = "DejaVuSans-Bold.ttf" if negrito else "DejaVuSans.ttf"
        return ImageFont.truetype(nome, tamanho)
    except OSError:
        return ImageFont.load_default()


def gerar_comprovante_png(saque: dict) -> bytes:
    W, H = 720, 900
    img = Image.new("RGB", (W, H), "#0e1116")
    d = ImageDraw.Draw(img)

    # Faixa superior
    d.rectangle([0, 0, W, 130], fill="#16a34a")

    f_titulo = _fonte(38, True)
    f_sub    = _fonte(22)
    f_label  = _fonte(20)
    f_valor  = _fonte(26, True)
    f_peq    = _fonte(18)

    d.text((40, 30), "✅  COMPROVANTE", font=f_titulo, fill="white")
    d.text((40, 80), "Saque realizado com sucesso", font=f_sub, fill="#dcfce7")

    # Bloco
    y = 180
    linhas = [
        ("Titular",  saque.get("titular_nome") or "-"),
        ("Banco",    saque.get("titular_banco") or "-"),
        ("Chave",    saque.get("chave_mascarada") or "-"),
        ("ID",       saque.get("txid") or "-"),
        ("Data",     (saque.get("criado_em") or datetime.now().strftime("%d/%m/%Y %H:%M"))[:16]),
    ]
    for label, val in linhas:
        d.text((40, y), label.upper(), font=f_label, fill="#94a3b8")
        d.text((40, y + 28), str(val), font=f_valor, fill="white")
        y += 90

    # Valor destacado
    y += 20
    d.rectangle([30, y, W - 30, y + 120], fill="#16a34a", outline=None)
    d.text((50, y + 20), "VALOR SACADO", font=f_label, fill="#dcfce7")
    d.text((50, y + 55), f"R$ {float(saque.get('valor') or 0):.2f}", font=_fonte(42, True), fill="white")

    # Rodapé
    d.text((40, H - 60), f"Emitido por {NOME_TITULAR_CONTA}", font=f_peq, fill="#64748b")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def gerar_comprovante_pdf(saque: dict) -> bytes:
    from fpdf import FPDF

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_fill_color(22, 163, 74)
    pdf.rect(0, 0, 210, 35, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_xy(15, 10)
    pdf.cell(0, 10, "COMPROVANTE DE SAQUE", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)

    def linha(label, val):
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(50, 8, label, border=0)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, str(val), border=0, ln=True)

    linha("Titular:", saque.get("titular_nome") or "-")
    linha("Banco:",   saque.get("titular_banco") or "-")
    linha("Chave:",   saque.get("chave_mascarada") or "-")
    linha("ID:",      saque.get("txid") or "-")
    linha("Data:",    (saque.get("criado_em") or datetime.now().strftime("%d/%m/%Y %H:%M"))[:16])
    linha("Valor:",   f"R$ {float(saque.get('valor') or 0):.2f}")
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 8, f"Emitido por {NOME_TITULAR_CONTA}", ln=True)

    return bytes(pdf.output())
