from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel


class ActivityResponse(BaseModel):
    id: int
    type: str
    description: str
    meta: Optional[Any] = None
    lead_id: Optional[int] = None
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedActivities(BaseModel):
    items: List[ActivityResponse]
    total: int
    page: int
    limit: int
    pages: int
