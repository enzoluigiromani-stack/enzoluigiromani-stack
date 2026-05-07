from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.lead import Lead
from app.models.pipeline_stage import PipelineStage
from app.schemas.lead import LeadResponse
from app.schemas.pipeline_stage import PipelineStageCreate, PipelineStageResponse

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.get("/stages", response_model=List[PipelineStageResponse])
def list_stages(db: Session = Depends(get_db)):
    return db.query(PipelineStage).order_by(PipelineStage.order).all()


@router.post("/stages", response_model=PipelineStageResponse, status_code=status.HTTP_201_CREATED)
def create_stage(stage: PipelineStageCreate, db: Session = Depends(get_db)):
    if db.query(PipelineStage).filter(PipelineStage.name == stage.name).first():
        raise HTTPException(status_code=409, detail=f"Etapa '{stage.name}' já existe")
    db_stage = PipelineStage(**stage.model_dump())
    db.add(db_stage)
    db.commit()
    db.refresh(db_stage)
    return db_stage


@router.get("/board")
def get_board(db: Session = Depends(get_db)):
    stages = db.query(PipelineStage).order_by(PipelineStage.order).all()
    board = []
    for stage in stages:
        leads = db.query(Lead).filter(Lead.stage_id == stage.id).all()
        board.append({
            "stage": jsonable_encoder(PipelineStageResponse.model_validate(stage)),
            "total": len(leads),
            "leads": [jsonable_encoder(LeadResponse.model_validate(l)) for l in leads],
        })
    return {"board": board}
