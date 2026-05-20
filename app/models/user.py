from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database.database import Base

ROLES = ("admin", "manager", "sales")


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String, nullable=False)
    email           = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role            = Column(String, default="admin")   # admin | manager | sales
    is_admin        = Column(Boolean, default=False)    # derivado de role; mantido por compatibilidade
    is_active       = Column(Boolean, default=True)
    workspace_id    = Column(Integer, ForeignKey("workspaces.id"), nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="users")
