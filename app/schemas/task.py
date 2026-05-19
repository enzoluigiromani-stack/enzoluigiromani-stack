from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class TaskCreate(BaseModel):
    lead_id: Optional[int] = None
    assigned_user_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    status: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    workspace_id: int
    lead_id: Optional[int] = None
    assigned_user_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    lead_name: Optional[str] = None
    assigned_user_name: Optional[str] = None

    model_config = {"from_attributes": True}


class PaginatedTasks(BaseModel):
    items: List[TaskResponse]
    total: int
    page: int
    limit: int
    pages: int
