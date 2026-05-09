from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database.database import Base


class WorkspaceSettings(Base):
    __tablename__ = "workspace_settings"

    id            = Column(Integer, primary_key=True, index=True)
    workspace_id  = Column(Integer, ForeignKey("workspaces.id"), unique=True, nullable=False)
    company_name  = Column(String, nullable=True)
    currency      = Column(String, default="BRL")
    timezone      = Column(String, default="America/Sao_Paulo")
    primary_color = Column(String, default="#6366f1")
    logo_url      = Column(String, nullable=True)

    workspace = relationship("Workspace", back_populates="settings")
