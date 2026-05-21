from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from app.database.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id           = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    type         = Column(String, nullable=False)          # lead_created|lead_moved|task_created|message_received
    title        = Column(String, nullable=False)
    message      = Column(Text, nullable=True)
    read         = Column(Boolean, default=False, nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
