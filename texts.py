# texts.py
from config import NOME_LOJA, CLIENTES_ATENDIDOS


# ---------- Módulo 1 ----------
def boas_vindas(user_id: int, saldo: float) -> str:
    return (
        f"📡 <b>Bem-vindo à {NOME_LOJA}!</b>\n"
        f"✨ A sua central de serviços com entrega 100% automática.\n"
        f"Pagou, recebeu. Sem filas, sem precisar falar com atendente, 24 horas por dia! ⚡\n\n"
        f"🛡 <b>Segurança e Suporte:</b>\n"
        f"Mais de {CLIENTES_ATENDIDOS} clientes já passaram por aqui.\n"
        f"Participe da nossa comunidade e veja as referências\n\n"
        f"● <b>Seus Dados:</b>\n"
        f"├ 👤 ID: <code>{user_id}</code>\n"
        f"└ 💰 Saldo Atual: <b>R$ {saldo:,.2f}</b>\n\n"
        f"👇 <b>COMO COMEÇAR:</b>\n"
        f"Clique no botão \"🛍 Comprar Produtos\" abaixo para ver nosso catálogo e escolher sua tela!"
    )


def bloqueio_canal() -> str:
    return (
        "🔒 <b>Acesso Bloqueado</b>\n\n"
        "Para utilizar o bot, é necessário entrar no nosso canal oficial.\n\n"
        "👉 Entre no canal abaixo e o acesso será liberado automaticamente."
    )


# ---------- Módulo 2 ----------
def texto_catalogo(saldo: float) -> str:
    return (
        f"⚡ <b>{NOME_LOJA}</b> | Catálogo de Serviços\n"
        f"────────────────────────\n"
        f"💰 | Saldo da Carteira: <b>R$ {saldo:,.2f}</b>\n\n"
        f"⬇️ Selecione uma categoria abaixo para ver nossos planos:"
    )


def texto_produto(p: dict, saldo: float) -> str:
    return (
        f"🔥 <b>OPORTUNIDADE EXCLUSIVA</b> 🔥\n"
        f"🚀 <b>{p['nome']}</b>\n\n"
        f"🟢 <b>DISPONÍVEL AGORA</b>\n"
        f"├ 💵 Preço: <b>R$ {p['preco']:.2f}</b>\n"
        f"├ 💰 Seu Saldo: <b>R$ {saldo:.2f}</b>\n"
        f"└ 📦 Estoque: <b>{p['estoque']}</b>\n\n"
        f"📝 <b>Descrição:</b>\n{p['descricao']}\n\n"
        f"📊 <b>Estatísticas em tempo real:</b>\n"
        f"⚡️ Já foram vendidas <b>{p['vendidos']}</b> unidades!\n"
        f"👀 <b>{p['vendo_agora']}</b> pessoas estão vendo isso agora.\n\n"
        f"🛡 Garantia: <b>{p['garantia']} dias</b>\n"
        f"✅ Compra segura. Ao adquirir, concorda com /termos"
    )


def texto_saldo_insuficiente(saldo: float, valor: float, faltam: float) -> str:
    return (
        f"❌ <b>Saldo insuficiente!</b>\n\n"
        f"💰 Seu saldo: <b>R$ {saldo:.2f}</b>\n"
        f"💵 Valor do produto: <b>R$ {valor:.2f}</b>\n"
        f"📉 Faltam: <b>R$ {faltam:.2f}</b>\n\n"
        f"💡 Deseja gerar um PIX no valor de <b>R$ {valor:.2f}</b> para completar a compra?"
    )


def texto_gerando_pagamento() -> str:
    return "⏳ <b>Gerando pagamento...</b>"


def texto_qr_pix(valor: float, txid: str) -> str:
    return (
        f"💠 <b>PIX gerado com sucesso!</b>\n\n"
        f"💵 Valor: <b>R$ {valor:.2f}</b>\n"
        f"🆔 ID: <code>{txid}</code>\n"
        f"⏰ Expira em: <b>30 minutos</b>\n\n"
        f"📋 Use o botão <b>Copiar PIX</b> para copiar o código ou escaneie o QR Code acima.\n\n"
        f"<i>Após pagar, clique em ⏰ AGUARDANDO PAGAMENTO.</i>"
    )


def texto_aguardando_nao_pago() -> str:
    return (
        "⚠️ <b>Pagamento não identificado</b>\n\n"
        "Nosso sistema viu que você não realizou o pagamento ainda.\n"
        "Se já pagou, aguarde alguns instantes e clique em ⏰ AGUARDANDO PAGAMENTO novamente."
    )


def texto_pago() -> str:
    return "✅ <b>PAGO</b>"


# ---------- Módulo 3 — 5B Comprar mais de um ----------
def texto_perguntar_qtd(estoque: int) -> str:
    return (
        f"<b>Quantos logins deseja comprar?</b>\n\n"
        f"📦 Estoque disponível: <b>{estoque}</b>\n\n"
        f"💡 Digite /cancelar a qualquer momento para sair."
    )


def texto_resultado_pedido(produto: dict, qtd: int, total: float, saldo: float) -> str:
    return (
        f"🛒 <b>RESULTADO DO PEDIDO</b>\n"
        f"🚀 <b>{produto['nome']}</b>\n"
        f"📦 Quantidade: <b>{qtd}</b>\n"
        f"💵 Preço unitário: <b>R$ {produto['preco']:.2f}</b>\n"
        f"💰 Total: <b>R$ {total:.2f}</b>\n"
        f"💰 Seu Saldo: <b>R$ {saldo:.2f}</b>"
    )


def texto_saldo_insuficiente_multi(saldo: float, total: float, faltam: float) -> str:
    return (
        f"❌ <b>Saldo insuficiente!</b>\n\n"
        f"💰 Seu saldo: <b>R$ {saldo:.2f}</b>\n"
        f"💵 Valor total: <b>R$ {total:.2f}</b>\n"
        f"📉 Faltam: <b>R$ {faltam:.2f}</b>\n\n"
        f"💡 Deseja gerar um PIX para completar a compra?"
    )


def texto_compra_cancelada() -> str:
    return (
        "❌ <b>Compra cancelada!</b>\n\n"
        "Operação de compra múltipla foi cancelada."
    )


def texto_qtd_invalida(estoque: int) -> str:
    return (
        f"⚠️ <b>Quantidade inválida.</b>\n\n"
        f"Digite um número entre 1 e {estoque} ou /cancelar para sair."
    )


# ---------- Módulo 3 — Seção 6 Entrega ----------
def _borrado(txt: str) -> str:
    return "•" * len(txt) if txt else "•" * 16


def texto_entrega(compra: dict, revelar: bool = False) -> str:
    email = compra["email"] if revelar else _borrado(compra["email"])
    senha = compra["senha"] if revelar else _borrado(compra["senha"])

    return (
        f"✅ <b>Produto realizado com sucesso!</b>\n\n"
        f"⏰ Data da compra: <b>{compra['data_compra']}</b>\n"
        f"📆 Vencimento: <b>{compra['data_vencimento']}</b>\n"
        f"💰 Valor: <b>R$ {compra['valor_total']:.2f}</b>\n"
        f"🎫 ID da compra: <code>{compra['id']}</code>\n"
        f"⚜️ Serviço: <b>{compra['produto_nome']}</b> (no seu email)\n"
        f"📧 Email: <code>{email}</code>\n"
        f"🔐 Senha: <code>{senha}</code>\n"
        f"📃 Nota: Use o botão abaixo para ativar:"
    )


# ---------- Módulo 3 — Seção 7 Perfil ----------
def texto_perfil(user_id: int, saldo: float, whatsapp: str, stats: dict) -> str:
    zap = whatsapp if whatsapp else "Não cadastrado"
    return (
        f"👤 <b>Meu perfil</b>\n\n"
        f"🔍 Veja aqui os detalhes da sua conta:\n\n"
        f"- 👤 <b>Informações:</b>\n"
        f"🆔 ID da Carteira: <code>{user_id}</code>\n"
        f"💰 Saldo Atual: <b>R$ {saldo:.2f}</b>\n"
        f"📲 Seu Whatsapp: <b>{zap}</b>\n\n"
        f"─── 📊 <b>Suas Movimentações:</b>\n"
        f"ー 🛒 Compras Realizadas: <b>{stats['qtd']}</b>\n"
        f"ー 💰 Total Gasto Em Compras: <b>R$ {stats['gasto']:.2f}</b>\n"
        f"ー 💠 Pix Inseridos: <b>R$ 0.00</b>\n"
        f"ー 🎁 Gifts Resgatados: <b>R$ 0.00</b>"
    )


# ---------- Módulo 3 — Seção 8 Histórico ----------
def texto_historico_vazio() -> str:
    return (
        "📜 <b>Histórico de Compras</b>\n\n"
        "Você não tem compras no bot. Quando comprar alguma conta, as informações dela ficarão exibidas aqui."
    )


def texto_historico_item(compra: dict, pagina: int, total: int) -> str:
    return (
        f"📜 <b>Histórico de Compras</b>  ·  📄 {pagina}/{total}\n\n"
        f"🎫 ID: <code>{compra['id']}</code>\n"
        f"🚀 <b>{compra['produto_nome']}</b>\n"
        f"📦 Quantidade: <b>{compra['quantidade']}</b>\n"
        f"💰 Valor: <b>R$ {compra['valor_total']:.2f}</b>\n"
        f"⏰ Comprado em: <b>{compra['data_compra']}</b>\n"
        f"📆 Vencimento: <b>{compra['data_vencimento']}</b>\n"
        f"🟢 Status: <b>{'Ativo' if compra['status'] == 'ativo' else 'Expirado'}</b>"
    )
