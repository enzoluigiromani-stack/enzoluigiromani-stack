from typing import Optional
from pydantic import BaseModel


class WorkspaceIntegrationsResponse(BaseModel):
    id: int
    workspace_id: int
    whatsapp_token: Optional[str] = None
    whatsapp_phone_id: Optional[str] = None
    meta_access_token: Optional[str] = None
    meta_pixel_id: Optional[str] = None
    sendgrid_api_key: Optional[str] = None
    sendgrid_from_email: Optional[str] = None
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_from_number: Optional[str] = None

    class Config:
        from_attributes = True


class WorkspaceIntegrationsUpdate(BaseModel):
    whatsapp_token: Optional[str] = None
    whatsapp_phone_id: Optional[str] = None
    meta_access_token: Optional[str] = None
    meta_pixel_id: Optional[str] = None
    sendgrid_api_key: Optional[str] = None
    sendgrid_from_email: Optional[str] = None
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_from_number: Optional[str] = None
