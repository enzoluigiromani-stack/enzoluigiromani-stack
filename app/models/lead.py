from datetime import datetime
from sqlalchemy import Column, Float, ForeignKey, Integer, String, DateTime, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.database import Base


class Lead(Base):
    __tablename__ = "leads"
    __table_args__ = (
        UniqueConstraint("email", "workspace_id", name="uq_leads_email_workspace"),
    )

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String, nullable=False)
    email        = Column(String, nullable=False, index=True)
    phone        = Column(String, nullable=True)
    source       = Column(String, nullable=True)
    status       = Column(String, default="novo")
    stage_id     = Column(Integer, ForeignKey("pipeline_stages.id"), nullable=True)
    budget       = Column(Float, nullable=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, nullable=True)

    # UTM tracking
    utm_source   = Column(String, nullable=True)
    utm_campaign = Column(String, nullable=True)
    utm_medium   = Column(String, nullable=True)
    utm_content  = Column(String, nullable=True)
    utm_term     = Column(String, nullable=True)

    # Ad attribution
    campaign_name      = Column(String, nullable=True)
    adset_name         = Column(String, nullable=True)
    ad_name            = Column(String, nullable=True)
    external_source_id = Column(String, nullable=True, index=True)

    # Tags automáticas (lista JSON: ['facebook', 'high_ticket', ...])
    tags = Column(JSON, nullable=True)

    stage     = relationship("PipelineStage", back_populates="leads")
    owner     = relationship("User")
    workspace = relationship("Workspace", back_populates="leads")
    tasks     = relationship("Task", back_populates="lead", cascade="all, delete-orphan")
    capture_events = relationship("LeadCaptureEvent", back_populates="lead")
