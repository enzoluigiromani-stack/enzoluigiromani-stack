from datetime import datetime
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.lead import Lead
from app.models.pipeline_stage import PipelineStage
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.lead import LeadCreate, LeadMoveRequest, LeadUpdate, LeadResponse
from app.services.activity_service import log_activity
from app.services.permissions import require_manager, require_sales
from app.services.workspace import require_workspace
from app.services.notifications import notify_new_lead, notify_lead_moved
from app.services.task_service import create_followup_task
from app.services import realtime
from app.services.notification_service import create_notification

router = APIRouter(prefix="/leads", tags=["leads"])


def _upsert_lead(db: Session, email: str, workspace_id: int, data: dict) -> tuple[Lead, bool]:
    existing = (
        db.query(Lead)
        .filter(Lead.email == email, Lead.workspace_id == workspace_id)
        .first()
    )
    if existing:
        for field, value in data.items():
            if value is not None:
                setattr(existing, field, value)
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing, False

    if not data.get("stage_id"):
        novo = (
            db.query(PipelineStage)
            .filter(PipelineStage.name == "novo", PipelineStage.workspace_id == workspace_id)
            .first()
        )
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
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    data = {**lead.model_dump(), "user_id": current_user.id, "workspace_id": workspace.id}
    db_lead, criado = _upsert_lead(db, lead.email, workspace.id, data)

    activity_type = "lead_created" if criado else "lead_updated"
    log_activity(
        db,
        workspace_id=workspace.id,
        type=activity_type,
        description=f"Lead {'criado' if criado else 'atualizado'}: {db_lead.name}",
        user_id=current_user.id,
        lead_id=db_lead.id,
        meta={"email": db_lead.email, "source": db_lead.source},
    )

    if criado:
        background_tasks.add_task(notify_new_lead, db_lead)
        lead_dict = jsonable_encoder(LeadResponse.model_validate(db_lead))
        background_tasks.add_task(realtime.broadcast_lead_created, workspace.id, lead_dict)
        background_tasks.add_task(
            create_notification, db, workspace.id,
            "lead_created", f"Novo lead: {db_lead.name}",
            f"Lead capturado via {db_lead.source or 'manual'}",
        )

    return {"message": "Lead criado" if criado else "Lead atualizado",
            "lead": jsonable_encoder(LeadResponse.model_validate(db_lead))}


@router.get("/", response_model=List[LeadResponse])
def list_leads(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    query = db.query(Lead).filter(Lead.workspace_id == workspace.id)
    if current_user.role == "sales":
        query = query.filter(Lead.user_id == current_user.id)
    return query.offset(skip).limit(limit).all()


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    query = db.query(Lead).filter(Lead.id == lead_id, Lead.workspace_id == workspace.id)
    if current_user.role == "sales":
        query = query.filter(Lead.user_id == current_user.id)
    lead = query.first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int,
    data: LeadUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    query = db.query(Lead).filter(Lead.id == lead_id, Lead.workspace_id == workspace.id)
    if current_user.role == "sales":
        query = query.filter(Lead.user_id == current_user.id)
    lead = query.first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    changed = list(data.model_dump(exclude_unset=True).keys())
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)

    log_activity(
        db,
        workspace_id=workspace.id,
        type="lead_updated",
        description=f"Lead atualizado: {lead.name}",
        user_id=current_user.id,
        lead_id=lead.id,
        meta={"changed_fields": changed},
    )
    lead_dict = jsonable_encoder(LeadResponse.model_validate(lead))
    background_tasks.add_task(realtime.broadcast_lead_updated, workspace.id, lead_dict)
    return lead


@router.patch("/{lead_id}/move")
def move_lead(
    lead_id: int,
    body: LeadMoveRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
    workspace: Workspace = Depends(require_workspace),
):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.workspace_id == workspace.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    old_stage = db.query(PipelineStage).filter(PipelineStage.id == lead.stage_id).first()
    stage = (
        db.query(PipelineStage)
        .filter(PipelineStage.id == body.stage_id, PipelineStage.workspace_id == workspace.id)
        .first()
    )
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")

    lead.stage_id = body.stage_id
    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)

    log_activity(
        db,
        workspace_id=workspace.id,
        type="lead_moved",
        description=f"Lead movido: {lead.name} → {stage.name}",
        user_id=current_user.id,
        lead_id=lead.id,
        meta={"from_stage": old_stage.name if old_stage else None, "to_stage": stage.name},
    )

    # Follow-up automático ao entrar em "contato"
    if stage.name == "contato":
        task = create_followup_task(db, workspace.id, lead, stage.name)
        log_activity(
            db,
            workspace_id=workspace.id,
            type="followup_created",
            description=f"Follow-up criado para {lead.name}",
            user_id=current_user.id,
            lead_id=lead.id,
            meta={"task_id": task.id, "due_date": str(task.due_date)},
        )

    background_tasks.add_task(notify_lead_moved, lead, stage.name)
    lead_dict = jsonable_encoder(LeadResponse.model_validate(lead))
    from_name = old_stage.name if old_stage else "?"
    background_tasks.add_task(
        realtime.broadcast_lead_moved, workspace.id, lead.id, from_name, stage.name, lead_dict
    )
    background_tasks.add_task(
        create_notification, db, workspace.id,
        "lead_moved", f"Lead movido: {lead.name}",
        f"{from_name} → {stage.name}",
    )
    return {"message": f"Lead movido para '{stage.name}'", "lead_id": lead_id,
            "stage": jsonable_encoder(stage)}


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(
    lead_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
    workspace: Workspace = Depends(require_workspace),
):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.workspace_id == workspace.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    db.delete(lead)
    db.commit()
    background_tasks.add_task(realtime.broadcast_lead_deleted, workspace.id, lead_id)
