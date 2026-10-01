# webapp/routes/idade.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from auth import get_telegram_user
from db import set_verificacao_idade

router = APIRouter(prefix="/api/idade", tags=["idade"])


@router.post("/verificar")
async def verificar_idade(
    frente: UploadFile = File(...),
    verso: UploadFile = File(...),
    user: dict = Depends(get_telegram_user),
):
    """
    Recebe as 2 fotos. Aprova automaticamente (mock).
    Substitua por IA/manual quando quiser.
    """
    frente_bytes = await frente.read()
    verso_bytes  = await verso.read()

    if len(frente_bytes) < 1024 or len(verso_bytes) < 1024:
        raise HTTPException(400, "Fotos inválidas")

    # ⚠️ Aprovação automática — troque por IA/manual depois
    aprovado = True
    motivo = ""

    set_verificacao_idade(
        user_id=user["id"],
        aprovado=aprovado,
        frente=frente_bytes,
        verso=verso_bytes,
        motivo=motivo,
    )

    return {"aprovado": aprovado, "motivo": motivo}
