from datetime import datetime
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.lead import Lead
from app.models.pipeline_stage import PipelineStage
from app.models.user import User
from app.schemas.lead import LeadCreate, LeadMoveRequest, LeadUpdate, LeadResponse
from app.services.auth import get_current_user
from app.services.notifications import notify_new_lead, notify_lead_moved

router = APIRouter(prefix="/leads", tags=["leads"])


def _upsert_lead(db: Session, email: str, data: dict) -> tuple[Lead, bool]:
    existing = db.query(Lead).filter(Lead.email == email).first()
    if existing:
        for field, value in data.items():
            if value is not None:
                setattr(existing, field, value)
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing, False

    if not data.get("stage_id"):
        novo = db.query(PipelineStage).filter(PipelineStage.name == "novo").first()
        if novo:
            data = {**data, "stage_id": novo.id}

    lead = Lead(**data)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead, True


@router.post("/", status_code=200)
def create_lead(
    lead: LeadCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = {**lead.model_dump(), "user_id": current_user.id}
    db_lead, criado = _upsert_lead(db, lead.email, data)
    if criado:
        background_tasks.add_task(notify_new_lead, db_lead)
    mensagem = "Lead criado" if criado else "Lead atualizado"
    return {"message": mensagem, "lead": jsonable_encoder(LeadResponse.model_validate(db_lead))}


@router.get("/", response_model=List[LeadResponse])
def list_leads(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Lead)
        .filter(Lead.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.user_id == current_user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int,
    data: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.user_id == current_user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)
    return lead


@router.patch("/{lead_id}/move")
def move_lead(
    lead_id: int,
    body: LeadMoveRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.user_id == current_user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    stage = db.query(PipelineStage).filter(PipelineStage.id == body.stage_id).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")
    lead.stage_id = body.stage_id
    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)
    background_tasks.add_task(notify_lead_moved, lead, stage.name)
    return {
        "message": f"Lead movido para '{stage.name}'",
        "lead_id": lead_id,
        "stage": jsonable_encoder(stage),
    }


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.user_id == current_user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    db.delete(lead)
    db.commit()
