from fastapi import APIRouter, Depends
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceResponse
from app.services.workspace import require_workspace

router = APIRouter(prefix="/workspace", tags=["workspace"])


@router.get("/me", response_model=WorkspaceResponse)
def get_my_workspace(workspace: Workspace = Depends(require_workspace)):
    return workspace
