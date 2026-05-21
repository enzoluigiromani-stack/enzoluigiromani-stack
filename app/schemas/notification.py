from datetime import datetime
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    workspace_id: int
    user_id: int | None
    type: str
    title: str
    message: str | None
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    workspace_id: int
    user_id: int | None = None
    type: str
    title: str
    message: str | None = None
