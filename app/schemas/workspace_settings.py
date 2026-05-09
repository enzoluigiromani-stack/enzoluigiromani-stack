from typing import Optional
from pydantic import BaseModel


class WorkspaceSettingsResponse(BaseModel):
    id: int
    workspace_id: int
    company_name: Optional[str] = None
    currency: str = "BRL"
    timezone: str = "America/Sao_Paulo"
    primary_color: str = "#6366f1"
    logo_url: Optional[str] = None

    class Config:
        from_attributes = True


class WorkspaceSettingsUpdate(BaseModel):
    company_name: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    primary_color: Optional[str] = None
    logo_url: Optional[str] = None
