from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


class LeadCaptureEventResponse(BaseModel):
    id:          int
    workspace_id: int
    lead_id:     Optional[int] = None
    source:      str
    processed:   bool
    error:       Optional[str] = None
    created_at:  datetime

    class Config:
        from_attributes = True


class CaptureEventListResponse(BaseModel):
    total: int
    items: list[LeadCaptureEventResponse]
