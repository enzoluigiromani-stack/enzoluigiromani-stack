from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database.database import Base


class WorkspaceIntegrations(Base):
    __tablename__ = "workspace_integrations"

    id           = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), unique=True, nullable=False)

    # WhatsApp Business API
    whatsapp_token    = Column(String, nullable=True)
    whatsapp_phone_id = Column(String, nullable=True)

    # Meta / Facebook
    meta_access_token = Column(String, nullable=True)
    meta_pixel_id     = Column(String, nullable=True)

    # E-mail — SendGrid
    sendgrid_api_key    = Column(String, nullable=True)
    sendgrid_from_email = Column(String, nullable=True)

    # SMS — Twilio
    twilio_account_sid  = Column(String, nullable=True)
    twilio_auth_token   = Column(String, nullable=True)
    twilio_from_number  = Column(String, nullable=True)

    workspace = relationship("Workspace", back_populates="integrations")
