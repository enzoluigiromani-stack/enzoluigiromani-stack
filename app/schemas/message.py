from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel


class MessageCreate(BaseModel):
    conversation_id: int
    content:         str
    message_type:    str = "text"   # text | image | file
    # sender_type é inferido do token (user) ou definido pelo sistema (lead/system)
    sender_type:     str = "user"


class MessageResponse(BaseModel):
    id:                  int
    conversation_id:     int
    sender_type:         str
    sender_id:           Optional[int] = None
    content:             str
    message_type:        str
    external_message_id: Optional[str] = None
    meta:                Optional[Any] = None
    created_at:          datetime
    delivered_at:        Optional[datetime] = None
    read_at:             Optional[datetime] = None

    class Config:
        from_attributes = True


class PaginatedMessages(BaseModel):
    items: List[MessageResponse]
    total: int
    page:  int
    limit: int
    pages: int
