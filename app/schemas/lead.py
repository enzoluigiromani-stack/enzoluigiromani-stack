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
    budget: Optional[float] = None

    # UTM tracking
    utm_source:   Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_medium:   Optional[str] = None
    utm_content:  Optional[str] = None
    utm_term:     Optional[str] = None

    # Ad attribution
    campaign_name:      Optional[str] = None
    adset_name:         Optional[str] = None
    ad_name:            Optional[str] = None
    external_source_id: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    budget: Optional[float] = None
    utm_source:   Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_medium:   Optional[str] = None
    utm_content:  Optional[str] = None
    utm_term:     Optional[str] = None
    campaign_name:      Optional[str] = None
    adset_name:         Optional[str] = None
    ad_name:            Optional[str] = None
    external_source_id: Optional[str] = None


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
