# utils/validadores.py
import re
import uuid


def _digitos(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def validar_cpf(cpf: str) -> bool:
    cpf = _digitos(cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in range(9, 11):
        soma = sum(int(cpf[n]) * ((i + 1) - n) for n in range(i))
        dig = (soma * 10) % 11
        if dig == 10:
            dig = 0
        if dig != int(cpf[i]):
            return False
    return True


def validar_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.\+\-]+@[\w\-]+\.[\w\.\-]+$", (email or "").strip()))


def validar_telefone(tel: str) -> bool:
    d = _digitos(tel)
    if d.startswith("55") and len(d) > 11:
        d = d[2:]
    if len(d) not in (10, 11):
        return False
    return 11 <= int(d[:2]) <= 99


def validar_uuid(s: str) -> bool:
    try:
        uuid.UUID((s or "").strip())
        return True
    except (ValueError, AttributeError):
        return False


def mascarar(tipo: str, chave: str) -> str:
    """Máscara estilo bancário."""
    tipo = (tipo or "").lower()
    if tipo == "cpf":
        d = _digitos(chave)
        return f"***.***.***-{d[-2:]}" if len(d) >= 2 else "***"
    if tipo == "email":
        nome, _, dominio = (chave or "").partition("@")
        if not nome:
            return "***"
        return f"{nome[0]}***@{dominio}" if dominio else "***"
    if tipo == "telefone":
        d = _digitos(chave)
        return f"({d[:2]}) *****-{d[-4:]}" if len(d) >= 6 else "***"
    if tipo == "aleatoria":
        s = (chave or "").strip()
        return f"{s[:4]}...{s[-4:]}" if len(s) > 10 else "***"
    return "***"
