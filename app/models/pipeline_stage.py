from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.database import Base


class PipelineStage(Base):
    __tablename__ = "pipeline_stages"
    __table_args__ = (
        UniqueConstraint("name", "workspace_id", name="uq_stages_name_workspace"),
    )

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String, nullable=False)
    order        = Column(Integer, nullable=False)
    color        = Column(String, nullable=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)

    leads     = relationship("Lead", back_populates="stage")
    workspace = relationship("Workspace", back_populates="stages")
