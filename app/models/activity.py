from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship
from app.database.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id           = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=True)
    lead_id      = Column(Integer, ForeignKey("leads.id"), nullable=True, index=True)
    type         = Column(String, nullable=False)
    description  = Column(String, nullable=False)
    meta         = Column(JSON, nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User")
    lead = relationship("Lead")
