from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from app.database.database import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, nullable=False)
    slug       = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users    = relationship("User", back_populates="workspace")
    leads    = relationship("Lead", back_populates="workspace")
    stages   = relationship("PipelineStage", back_populates="workspace")
    settings     = relationship("WorkspaceSettings", back_populates="workspace", uselist=False)
    integrations = relationship("WorkspaceIntegrations", back_populates="workspace", uselist=False)
