from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.schemas.pipeline_stage import PipelineStageResponse


class LeadBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = "novo"


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None


class LeadMoveRequest(BaseModel):
    stage_id: int


class LeadResponse(LeadBase):
    id: int
    stage_id: Optional[int] = None
    stage: Optional[PipelineStageResponse] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
