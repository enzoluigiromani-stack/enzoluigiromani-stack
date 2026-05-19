from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id               = Column(Integer, primary_key=True, index=True)
    workspace_id     = Column(Integer, ForeignKey("workspaces.id"), nullable=False, index=True)
    lead_id          = Column(Integer, ForeignKey("leads.id"), nullable=True, index=True)
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    title            = Column(String, nullable=False)
    description      = Column(Text, nullable=True)
    status           = Column(String, default="pending", nullable=False, index=True)  # pending|completed|overdue
    priority         = Column(String, default="medium", nullable=False)               # low|medium|high
    due_date         = Column(DateTime, nullable=True, index=True)
    completed_at     = Column(DateTime, nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow, nullable=False)

    workspace     = relationship("Workspace")
    lead          = relationship("Lead", foreign_keys=[lead_id], back_populates="tasks")
    assigned_user = relationship("User", foreign_keys=[assigned_user_id])
