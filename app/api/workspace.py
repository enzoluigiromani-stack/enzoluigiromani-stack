from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_settings import WorkspaceSettings
from app.schemas.workspace import WorkspaceResponse
from app.schemas.workspace_settings import WorkspaceSettingsResponse, WorkspaceSettingsUpdate
from app.services.permissions import require_admin, require_sales
from app.services.workspace import require_workspace

router = APIRouter(prefix="/workspace", tags=["workspace"])


@router.get("/me", response_model=WorkspaceResponse)
def get_my_workspace(workspace: Workspace = Depends(require_workspace)):
    return workspace


@router.get("/settings", response_model=WorkspaceSettingsResponse)
def get_settings(
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    _: User = Depends(require_admin),
):
    settings = db.query(WorkspaceSettings).filter(
        WorkspaceSettings.workspace_id == workspace.id
    ).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Configurações não encontradas")
    return settings


@router.put("/settings", response_model=WorkspaceSettingsResponse)
def update_settings(
    data: WorkspaceSettingsUpdate,
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    _: User = Depends(require_admin),
):
    settings = db.query(WorkspaceSettings).filter(
        WorkspaceSettings.workspace_id == workspace.id
    ).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Configurações não encontradas")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)

    db.commit()
    db.refresh(settings)
    return settings
