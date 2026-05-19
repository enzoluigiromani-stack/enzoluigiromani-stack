from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ConversationCreate(BaseModel):
    lead_id:          Optional[int] = None
    channel:          str           # whatsapp | email | sms
    subject:          Optional[str] = None
    assigned_user_id: Optional[int] = None


class ConversationUpdate(BaseModel):
    status:           Optional[str] = None   # open | closed
    assigned_user_id: Optional[int] = None
    subject:          Optional[str] = None


class ConversationResponse(BaseModel):
    id:               int
    workspace_id:     int
    lead_id:          Optional[int] = None
    assigned_user_id: Optional[int] = None
    channel:          str
    status:           str
    subject:          Optional[str] = None
    external_id:      Optional[str] = None
    last_message_at:  Optional[datetime] = None
    created_at:       datetime
    updated_at:       Optional[datetime] = None
    closed_at:        Optional[datetime] = None
    # campos enriquecidos (preenchidos pelo endpoint, não pelo ORM)
    lead_name:        Optional[str] = None
    lead_email:       Optional[str] = None
    lead_phone:       Optional[str] = None

    class Config:
        from_attributes = True


class PaginatedConversations(BaseModel):
    items: List[ConversationResponse]
    total: int
    page:  int
    limit: int
    pages: int
