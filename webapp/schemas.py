# webapp/schemas.py
from pydantic import BaseModel, Field


class AuthIn(BaseModel):
    initData: str


class RecargaIn(BaseModel):
    valor: float = Field(..., gt=0)


class ItemCompra(BaseModel):
    produto_id: int
    qtd: int = Field(1, ge=1)


class CompraSaldoIn(BaseModel):
    itens: list[ItemCompra]


class CompraPixIn(BaseModel):
    itens: list[ItemCompra]


class CarrinhoAbertoIn(BaseModel):
    produto_id: int


class AdminLoginIn(BaseModel):
    senha: str
