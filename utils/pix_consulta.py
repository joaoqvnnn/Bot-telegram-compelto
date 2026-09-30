# utils/pix_consulta.py
"""
Mock de consulta de chave PIX.
Substitua consultar_chave() pela chamada real do seu PSP / Bacen DICT.
"""

MOCK_BANCOS = ["BANCO EXEMPLO S.A.", "BANCO DIGITAL LTDA", "CAIXA EXEMPLO"]


async def consultar_chave(tipo: str, chave: str) -> dict | None:
    """
    Retorna {'nome': str, 'banco': str} ou None se não encontrado.
    ⚠️ Mock — troque por integração real.
    """
    if not chave:
        return None
    # Simulação determinística
    return {
        "nome": "TITULAR DA CHAVE PIX",
        "banco": MOCK_BANCOS[len(chave) % len(MOCK_BANCOS)],
    }
