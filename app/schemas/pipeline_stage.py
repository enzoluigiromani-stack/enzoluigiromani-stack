from typing import Optional
from pydantic import BaseModel


class PipelineStageCreate(BaseModel):
    name: str
    order: int
    color: Optional[str] = None


class PipelineStageResponse(BaseModel):
    id: int
    name: str
    order: int
    color: Optional[str] = None

    class Config:
        from_attributes = True
