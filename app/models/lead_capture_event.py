from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship
from app.database.database import Base


class LeadCaptureEvent(Base):
    __tablename__ = "lead_capture_events"

    id           = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False, index=True)
    lead_id      = Column(Integer, ForeignKey("leads.id"), nullable=True, index=True)
    raw_payload  = Column(JSON, nullable=False)
    source       = Column(String, nullable=False)          # meta_lead_ads | custom | landing_page
    processed    = Column(Boolean, default=False, nullable=False)
    error        = Column(String, nullable=True)           # mensagem se o parse falhar
    created_at   = Column(DateTime, default=datetime.utcnow, index=True)

    workspace = relationship("Workspace")
    lead      = relationship("Lead", back_populates="capture_events")
