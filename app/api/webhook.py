import os
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.workspace import Workspace
from app.schemas.lead import LeadCreate, LeadResponse
from app.api.leads import _upsert_lead

router = APIRouter(prefix="/webhook", tags=["webhook"])

_SECRET = os.getenv("WEBHOOK_SECRET", "")


@router.post("/leads/{workspace_slug}", status_code=status.HTTP_200_OK)
def webhook_lead(
    workspace_slug: str,
    payload: LeadCreate,
    db: Session = Depends(get_db),
    x_webhook_secret: str | None = Header(default=None),
):
    """
    Recebe leads de fontes externas (formulários, Facebook Lead Ads, etc.).
    O workspace é identificado pelo slug na URL: POST /webhook/leads/{workspace_slug}
    """
    if _SECRET and x_webhook_secret != _SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    workspace = db.query(Workspace).filter(Workspace.slug == workspace_slug).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")

    data = {**payload.model_dump(), "workspace_id": workspace.id}
    lead, criado = _upsert_lead(db, payload.email, workspace.id, data)
    return {
        "status": "ok",
        "acao": "criado" if criado else "atualizado",
        "lead": jsonable_encoder(LeadResponse.model_validate(lead)),
    }
