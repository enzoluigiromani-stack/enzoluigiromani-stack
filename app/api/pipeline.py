from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.lead import Lead
from app.models.pipeline_stage import PipelineStage
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.lead import LeadResponse
from app.schemas.pipeline_stage import PipelineStageCreate, PipelineStageUpdate, PipelineStageResponse
from app.services.activity_service import log_activity
from app.services.permissions import require_manager, require_sales
from app.services.workspace import require_workspace
from app.services import realtime

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.get("/stages", response_model=List[PipelineStageResponse])
def list_stages(
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    _: User = Depends(require_sales),
):
    return (
        db.query(PipelineStage)
        .filter(PipelineStage.workspace_id == workspace.id)
        .order_by(PipelineStage.order)
        .all()
    )


@router.post("/stages", response_model=PipelineStageResponse, status_code=status.HTTP_201_CREATED)
def create_stage(
    stage: PipelineStageCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    user: User = Depends(require_manager),
):
    if (
        db.query(PipelineStage)
        .filter(PipelineStage.name == stage.name, PipelineStage.workspace_id == workspace.id)
        .first()
    ):
        raise HTTPException(status_code=409, detail=f"Etapa '{stage.name}' já existe")
    db_stage = PipelineStage(**stage.model_dump(), workspace_id=workspace.id)
    db.add(db_stage)
    db.commit()
    db.refresh(db_stage)

    log_activity(
        db,
        workspace_id=workspace.id,
        type="stage_created",
        description=f"Etapa criada: {db_stage.name}",
        user_id=user.id,
        meta={"stage_name": db_stage.name, "color": db_stage.color},
    )
    stage_dict = jsonable_encoder(PipelineStageResponse.model_validate(db_stage))
    background_tasks.add_task(realtime.broadcast_stage_created, workspace.id, stage_dict)
    return db_stage


@router.put("/stages/{stage_id}", response_model=PipelineStageResponse)
def update_stage(
    stage_id: int,
    stage_data: PipelineStageUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    user: User = Depends(require_manager),
):
    stage = (
        db.query(PipelineStage)
        .filter(PipelineStage.id == stage_id, PipelineStage.workspace_id == workspace.id)
        .first()
    )
    if not stage:
        raise HTTPException(status_code=404, detail="Estágio não encontrado")

    for field, value in stage_data.model_dump(exclude_unset=True).items():
        setattr(stage, field, value)

    db.commit()
    db.refresh(stage)
    stage_dict = jsonable_encoder(PipelineStageResponse.model_validate(stage))
    background_tasks.add_task(realtime.broadcast_stage_updated, workspace.id, stage_dict)
    return stage


@router.delete("/stages/{stage_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stage(
    stage_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    _: User = Depends(require_manager),
):
    stage = (
        db.query(PipelineStage)
        .filter(PipelineStage.id == stage_id, PipelineStage.workspace_id == workspace.id)
        .first()
    )
    if not stage:
        raise HTTPException(status_code=404, detail="Estágio não encontrado")

    # Desvincula leads antes de excluir o estágio
    db.query(Lead).filter(Lead.stage_id == stage_id).update({"stage_id": None})
    db.delete(stage)
    db.commit()
    background_tasks.add_task(realtime.broadcast_stage_deleted, workspace.id, stage_id)


@router.get("/board")
def get_board(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    stages = (
        db.query(PipelineStage)
        .filter(PipelineStage.workspace_id == workspace.id)
        .order_by(PipelineStage.order)
        .all()
    )
    board = []
    for stage in stages:
        q = db.query(Lead).filter(Lead.stage_id == stage.id, Lead.workspace_id == workspace.id)
        if current_user.role == "sales":
            q = q.filter(Lead.user_id == current_user.id)
        leads = q.all()
        board.append({
            "stage": jsonable_encoder(PipelineStageResponse.model_validate(stage)),
            "total": len(leads),
            "leads": [jsonable_encoder(LeadResponse.model_validate(l)) for l in leads],
        })
    return board
