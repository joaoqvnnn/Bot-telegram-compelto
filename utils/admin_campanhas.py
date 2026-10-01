# utils/admin_campanhas.py
"""
Funções que o Painel Admin vai chamar para:
  • criar/enviar campanhas agendadas
  • simular os textos padrão (editáveis)
  • ligar/desligar timers
"""
from database import (
    criar_campanha, set_config, get_config,
)


# ============================================================
# ⚙️ CONFIGURAÇÕES RÁPIDAS (chamáveis do painel)
# ============================================================
def set_timer_carrinho(minutos: int):
    """Define quantos minutos até avisar do carrinho abandonado."""
    set_config("carrinho_minutos", str(minutos))


def ativar_carrinho(ativo: bool):
    set_config("carrinho_ativo", "1" if ativo else "0")


def ativar_pix_expirado(ativo: bool):
    set_config("pix_expirado_ativo", "1" if ativo else "0")


# ============================================================
# 📢 CRIAR CAMPANHAS — exemplos prontos
# ============================================================
def campanha_promocao_produto(produto_id: int, texto: str, foto_url: str = "", agendado_para=None):
    """Promoção com botão que abre DIRETO no produto."""
    return criar_campanha(
        tipo="promocao",
        titulo="Promoção",
        texto=texto,
        foto_url=foto_url,
        botoes=[{"texto": "🔥 Aproveitar agora", "payload": f"prod_{produto_id}"}],
        agendado_para=agendado_para,
    )


def campanha_abastecido(texto: str, produto_id: int | None = None, foto_url: str = "", agendado_para=None):
    """
    Se produto_id informado → botão vai DIRETO ao produto.
    Senão → botão abre o catálogo completo.
    """
    payload = f"prod_{produto_id}" if produto_id else "cat"
    label = "📱 CLIQUE AQUI" if produto_id else "📱 VER PROMOÇÃO"
    return criar_campanha(
        tipo="abastecido",
        titulo="Bot Abastecido",
        texto=texto,
        foto_url=foto_url,
        botoes=[{"texto": label, "payload": payload}],
        agendado_para=agendado_para,
    )


def campanha_afiliados(texto: str, foto_url: str = "", agendado_para=None):
    return criar_campanha(
        tipo="afiliado",
        titulo="Sistema de Afiliados",
        texto=texto,
        foto_url=foto_url,
        botoes=[{"texto": "👥 Ver Sistema", "payload": "afiliados"}],
        agendado_para=agendado_para,
    )


def campanha_giftcard(texto: str, foto_url: str = "", agendado_para=None):
    return criar_campanha(
        tipo="gift",
        titulo="Resgate Gift Card",
        texto=texto,
        foto_url=foto_url,
        botoes=[{"texto": "🎁 Resgatar Gift Card", "payload": "gift"}],
        agendado_para=agendado_para,
    )


def campanha_custom(texto: str, botoes: list, foto_url: str = "", agendado_para=None):
    """
    Campanha 100% customizada.
    botoes: [{"texto": "Texto", "payload": "prod_5"}, {"texto": "Ver site", "url": "https://..."}]
    """
    return criar_campanha(
        tipo="promocao",
        titulo="Custom",
        texto=texto,
        foto_url=foto_url,
        botoes=botoes,
        agendado_para=agendado_para,
    )


# ============================================================
# 📌 EXEMPLOS (rode no Admin ou num script)
# ============================================================
EXEMPLO_BOT_ABASTECIDO = """✅ <b>BOT ABASTECIDO!</b>

🔥 Acabamos de abastecer nosso bot e você já pode garantir o seu streaming favorito para o fim de semana.

📱 Disney Padrão — R$ 2,90
📱 Disney Premium — R$ 7,90
🔴 Globoplay + Canais — R$ 3,90
🔴 Globoplay + cs + premiere + telecine — R$ 11,90
📱 Hbo Max — R$ 7,90
📱 Netflix Premium 4K — R$ 14,90
📱 Netflix Padrão — R$ 9,90
🔴 Sky+ Completa (espn,max,paramo,premier,telec,etc...) — R$ 11,90

⚠️ Poucas unidades disponíveis!
⚠️ Descontos disponíveis até acabar o estoque

🌟 Participe de nossa comunidade e fique por dentro de todas as promoções que estão rolando:"""

EXEMPLO_PROMO_HBO = """😍 <b>O queridinho de vocês finalmente voltou!!!</b>

HBO Max (NO SEU EMAIL)
✅ Apenas <b>R$ 4,90</b>

🗓 Duração: 30 Dias
🔒 Garantia: 30 Dias
🔒 Compra segura, liberação imediata
🔗 Ativação via link, direto na sua conta

⬇️ Clique abaixo e aproveite agora:"""

EXEMPLO_SKY_COMPLETA = """😳 <b>O que você procurava chegou!</b>

🚀 <b>SKY + Hbo Max + Disney + Paramount + Premiere + Telecine + Combate + Sportv + Nickelodeon</b>
🔥 <b>SKY+ COMPLETA</b>

💰 Apenas <b>R$ 11,90</b>

😨 Pouquíssimas unidades disponível!
⌛️ Promoção válida enquanto durar o estoque!"""
