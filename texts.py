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


# ============== MÓDULO 4 ==============

# ---------- 9. GIFT CARD ----------
def texto_gift_pedir() -> str:
    return (
        "🎁 <b>RESGATAR GIFT CARD</b>\n\n"
        "Digite o código do seu gift card abaixo:\n"
        "Exemplo: <code>ABC123XYZ456</code>"
    )


def texto_gift_invalido() -> str:
    return "❌ <b>Gift não encontrado.</b>"


def texto_gift_ok(valor: float, produto_nome: str | None) -> str:
    linha_prod = f"\n🎁 Produto vinculado: <b>{produto_nome}</b>" if produto_nome else ""
    return (
        f"✅ <b>Gift Card resgatado!</b>\n\n"
        f"💰 Valor creditado: <b>R$ {valor:.2f}</b>{linha_prod}"
    )


# ---------- 10. ALTERAR DADOS ----------
def texto_alterar_dados_atual(atual: str) -> str:
    return (
        "✏️ <b>ALTERAR DADOS</b>\n\n"
        f"📲 Whatsapp atual: <b>{atual or 'Não cadastrado'}</b>\n\n"
        "Envie o novo número com DDD (ex: <code>11987654321</code>).\n"
        "Para remover, envie: <code>remover</code>\n\n"
        "💡 Digite /cancelar para sair."
    )


def texto_alterar_dados_invalido() -> str:
    return "❌ <b>Número inválido.</b> Envie DDD + número (10 ou 11 dígitos) ou <code>remover</code>."


def texto_alterar_dados_ok(novo: str) -> str:
    if novo:
        return f"✅ <b>Whatsapp atualizado!</b>\n\n📲 Novo número: <b>{novo}</b>"
    return "✅ <b>Whatsapp removido com sucesso.</b>"


# ---------- 11. RECARGA ----------
def texto_recarga_menu() -> str:
    return (
        "💠 Opte por PIX Rápido para que seu saldo seja creditado imediatamente.\n"
        "💰 Selecione uma opção para recarregar:"
    )


def texto_recarga_pedir_valor() -> str:
    from database import get_config
    minimo = float(get_config("recarga_minima", "4.00"))
    bonus_ativo = get_config("recarga_bonus_ativo", "1") == "1"
    bonus_pct = get_config("recarga_bonus_pct", "10")
    bonus_min = float(get_config("recarga_bonus_min", "10.00"))

    base = (
        "ℹ️ Informe o valor que deseja recarregar:\n"
        f"🔻 Recarga mínima: <b>R$ {minimo:.2f}</b>\n\n"
        "⚠️ Por favor, envie o valor que deseja recarregar agora.\n"
        "Ao realizar um depósito você declara ter lido e estar de acordo com nossos /termos"
    )
    if bonus_ativo:
        base += (
            f"\n\n🎁 Bônus de recarga: <b>{bonus_pct}%</b>\n"
            f"❗ Recarga mínima para ganhar o bônus: <b>R$ {bonus_min:.2f}</b>"
        )
    return base


def texto_recarga_qr(valor: float, bonus: float, saldo_atual: float, txid: str) -> str:
    saldo_futuro = saldo_atual + valor + bonus
    linhas = [
        "💠 <b>PIX de recarga gerado!</b>\n",
        f"💵 Valor: <b>R$ {valor:.2f}</b>",
    ]
    if bonus > 0:
        linhas.append(f"🎁 Bônus: <b>R$ {bonus:.2f}</b>")
    linhas += [
        f"💰 Saldo atual: <b>R$ {saldo_atual:.2f}</b>",
        f"💸 Saldo após pagamento: <b>R$ {saldo_futuro:.2f}</b>",
        f"🆔 ID da recarga: <code>{txid}</code>",
        "⏰ Expira em: <b>30 minutos</b>",
    ]
    return "\n".join(linhas)


def texto_recarga_ok(valor: float, bonus: float, saldo_novo: float) -> str:
    linhas = [
        "✅ <b>Recarga realizada com sucesso!</b>\n",
        f"💵 Valor: <b>R$ {valor:.2f}</b>",
    ]
    if bonus > 0:
        linhas.append(f"🎁 Bônus: <b>R$ {bonus:.2f}</b>")
    linhas.append(f"💰 Novo saldo: <b>R$ {saldo_novo:.2f}</b>")
    return "\n".join(linhas)


# ---------- 12. AFILIADOS ----------
def texto_afiliado_inativo(comissao: float, saque_min: float) -> str:
    return (
        "💰 <b>PROGRAMA DE AFILIADOS</b>\n\n"
        "⚙️ Status: ❌ <b>Inativo</b>\n"
        f"🧲 Comissão: <b>{comissao:.1f}%</b>\n"
        f"💰 Saque mínimo: <b>R$ {saque_min:.2f}</b>\n\n"
        "ℹ️ <b>INFO:</b> Seus indicados continuarão gerando comissão para sempre."
    )


def texto_afiliado_ativo(af: dict, link: str, saque_min: float) -> str:
    indicacoes = af["indicacoes"]
    media = (af["total_ganho"] / indicacoes) if indicacoes else 0.0
    proxima = 5 - (indicacoes % 5) if indicacoes % 5 else 5
    nivel = "Iniciante" if indicacoes < 5 else ("Bronze" if indicacoes < 20 else "Prata")

    return (
        "💰 <b>PROGRAMA DE AFILIADOS</b>\n\n"
        "⚙️ Status: ✅ <b>Ativo</b>\n"
        f"🧲 Sua comissão: <b>{af['comissao']:.1f}%</b> (de todas recargas do indicado)\n\n"
        f"👥 Indicações: <b>{indicacoes}</b>\n"
        f"🪙 Total ganho: <b>R$ {af['total_ganho']:.2f}</b>\n"
        f"📊 Média: <b>R$ {media:.2f}</b>\n"
        f"💰 Saque mínimo: <b>R$ {saque_min:.2f}</b>\n\n"
        f"🌱| Nível: <b>{nivel}</b>\n"
        f"🎯 Próxima meta: <b>5</b> ({proxima} restantes)\n\n"
        "ℹ️ <b>INFO:</b> Seus indicados continuarão gerando comissão para sempre.\n\n"
        f"🔗 <b>Seu link:</b>\n<code>{link}</code>"
    )


# ============== MÓDULO 5 ==============

def _saudacao() -> str:
    from datetime import datetime
    h = datetime.now().hour
    if 5 <= h < 12:
        return "🌅 Bom dia"
    if 12 <= h < 18:
        return "🌇 Boa tarde"
    return "🌙 Boa noite"


# ---------- 14.1 ----------
def texto_sem_senha() -> str:
    return (
        "🔐 <b>Você ainda não cadastrou sua senha de saque.</b>\n\n"
        "Para realizar saques, é necessário cadastrar uma senha de 6 dígitos."
    )


# ---------- 14.2 ----------
def texto_pedir_chave() -> str:
    return "💸 Me informe sua chave PIX para qual você deseja receber seu pagamento:"


# ---------- 14.3 ----------
def texto_cadastrar_chave(tipo_label: str) -> str:
    return f"<b>Cadastre o seu {tipo_label} como chave de saque:</b>"


def texto_chave_invalida(tipo_label: str) -> str:
    return f"❌ <b>{tipo_label} inválido.</b> Envie novamente."


# ---------- 14.4 ----------
def texto_confirma_chave(nome: str, banco: str, tipo_label: str, mascarada: str) -> str:
    return (
        "Confirma essa é sua chave?\n"
        f"👤 Nome: <b>{nome}</b>\n"
        f"🏦 Banco: <b>{banco}</b>\n"
        f"🆔 {tipo_label}: <code>{mascarada}</code>"
    )


# ---------- 14.5 ----------
def texto_tela_saque(nome: str, saldo: float, saque_min: float) -> str:
    return (
        f"{_saudacao()}, <b>{nome}</b>!\n\n"
        f"💸 Quando você deseja sacar hoje?\n"
        f"💰 Saldo disponível: <b>R$ {saldo:.2f}</b>\n"
        f"💵 Saque mínimo: <b>R$ {saque_min:.2f}</b>"
    )


# ---------- 14.6 ----------
def texto_pedir_valor_saque(saldo: float, saque_min: float) -> str:
    return (
        "💸 <b>Qual valor você deseja sacar?</b>\n\n"
        f"💰 Saldo disponível: <b>R$ {saldo:.2f}</b>\n"
        f"💵 Saque mínimo: <b>R$ {saque_min:.2f}</b>"
    )


# ---------- 14.7 ----------
def texto_confirmar_saque(nome: str, banco: str, chave_mascarada: str, valor: float) -> str:
    return (
        "💰 <b>Confirme os dados do seu saque:</b>\n\n"
        f"👤 Nome: <b>{nome}</b>\n"
        f"🏦 Banco: <b>{banco}</b>\n"
        f"🆔 Chave: <code>{chave_mascarada}</code>\n"
        f"💵 Valor: <b>R$ {valor:.2f}</b>\n\n"
        "⚠️ Confira os dados antes de confirmar."
    )


# ---------- 14.8 ----------
def texto_pedir_senha() -> str:
    return "🔐 <b>Digite sua senha de 6 dígitos para confirmar o saque:</b>"


# ---------- 14.9 ----------
def texto_senha_errada() -> str:
    return "❌ <b>Senha incorreta! Tente novamente.</b>"


def texto_saque_processando() -> str:
    return "⏳ <b>Saque em processamento...</b>"


def texto_saque_ok() -> str:
    return "✅ <b>Saque realizado com sucesso!</b>"


# ---------- 15. Cadastro de senha (temporário até Mini App) ----------
def texto_cadastrar_senha_pedir() -> str:
    return (
        "🔐 <b>Cadastrar Senha de Saque</b>\n\n"
        "Envie uma senha de <b>6 dígitos numéricos</b>.\n"
        "💡 Essa senha será pedida a cada saque.\n\n"
        "Digite /cancelar para sair."
    )


def texto_cadastrar_senha_ok() -> str:
    return "✅ <b>Senha cadastrada com sucesso!</b>"
