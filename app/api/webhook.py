import os
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.lead import LeadCreate, LeadResponse
from app.api.leads import _upsert_lead

router = APIRouter(prefix="/webhook", tags=["webhook"])

_SECRET = os.getenv("WEBHOOK_SECRET", "")


@router.post("/leads", status_code=status.HTTP_200_OK)
def webhook_lead(
    payload: LeadCreate,
    db: Session = Depends(get_db),
    x_webhook_secret: str | None = Header(default=None),
):
    """
    Recebe leads de fontes externas (formulários, Facebook Lead Ads, etc.).
    - Se o e-mail já existe: atualiza os dados e retorna acao='atualizado'.
    - Se é novo: cria o lead e retorna acao='criado'.
    - Proteção opcional: envie o header X-Webhook-Secret com o valor da
      variável de ambiente WEBHOOK_SECRET.
    """
    if _SECRET and x_webhook_secret != _SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    lead, criado = _upsert_lead(db, payload.email, payload.model_dump())
    return {
        "status": "ok",
        "acao": "criado" if criado else "atualizado",
        "lead": jsonable_encoder(LeadResponse.model_validate(lead)),
    }
