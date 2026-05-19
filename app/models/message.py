from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from app.database.database import Base


class Message(Base):
    __tablename__ = "messages"

    id              = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)

    # user | lead | system
    sender_type = Column(String, nullable=False)
    # user_id ou lead_id dependendo do sender_type
    sender_id   = Column(Integer, nullable=True)

    content      = Column(Text, nullable=False)
    # text | image | file
    message_type = Column(String, default="text", nullable=False)

    # ID da mensagem no sistema externo (Twilio SID, SendGrid message-id, etc.)
    external_message_id = Column(String, nullable=True, index=True)

    # Dados extras por canal (status de entrega, URL de mídia, headers, etc.)
    meta = Column(JSON, nullable=True)

    created_at   = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at      = Column(DateTime, nullable=True)

    conversation = relationship("Conversation", back_populates="messages")
