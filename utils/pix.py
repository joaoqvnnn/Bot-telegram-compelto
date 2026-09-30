# utils/pix.py
import io
import uuid
import qrcode

from database import criar_pagamento


def gerar_pix_qr(user_id: int, produto_id: int, valor: float):
    """
    Gera um PIX (placeholder) e retorna (txid, copia_cola, png_bytes).
    Substitua o payload por um gerador EMV real quando integrar o gateway.
    """
    txid = uuid.uuid4().hex[:16].upper()

    # ⚠️ Copia-e-cola PLACEHOLDER — troque pelo EMV real do seu PSP
    copia_cola = f"00020126PIX-PLACEHOLDER{txid}VALOR{valor:.2f}"

    criar_pagamento(txid, user_id, produto_id, valor, copia_cola)

    img = qrcode.make(copia_cola)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return txid, copia_cola, buf.getvalue()
