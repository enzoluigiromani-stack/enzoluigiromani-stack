from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id               = Column(Integer, primary_key=True, index=True)
    workspace_id     = Column(Integer, ForeignKey("workspaces.id"), nullable=False, index=True)
    lead_id          = Column(Integer, ForeignKey("leads.id"), nullable=True, index=True)
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # whatsapp | email | sms
    channel  = Column(String, nullable=False, index=True)
    # open | closed
    status   = Column(String, default="open", nullable=False, index=True)

    subject             = Column(String, nullable=True)   # assunto para email
    external_id         = Column(String, nullable=True)   # thread/conversation ID externo

    last_message_at = Column(DateTime, nullable=True, index=True)
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at      = Column(DateTime, nullable=True)
    closed_at       = Column(DateTime, nullable=True)

    workspace     = relationship("Workspace")
    lead          = relationship("Lead", back_populates="conversations")
    assigned_user = relationship("User", foreign_keys=[assigned_user_id])
    messages      = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )
