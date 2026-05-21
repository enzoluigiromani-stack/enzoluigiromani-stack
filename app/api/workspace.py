from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_settings import WorkspaceSettings
from app.models.workspace_integrations import WorkspaceIntegrations
from app.schemas.user import UserResponse, UserInvite, UserRoleUpdate
from app.schemas.workspace import WorkspaceResponse
from app.schemas.workspace_settings import WorkspaceSettingsResponse, WorkspaceSettingsUpdate
from app.schemas.workspace_integrations import WorkspaceIntegrationsResponse, WorkspaceIntegrationsUpdate
from app.services.auth import hash_password
from app.services.permissions import require_admin, require_manager, require_sales
from app.services.workspace import require_workspace
from app.services import realtime

router = APIRouter(prefix="/workspace", tags=["workspace"])


# ── Workspace ────────────────────────────────────────────────────────────────

@router.get("/me", response_model=WorkspaceResponse)
def get_my_workspace(workspace: Workspace = Depends(require_workspace)):
    return workspace


# ── Settings ─────────────────────────────────────────────────────────────────

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


# ── Team ─────────────────────────────────────────────────────────────────────

@router.get("/users", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    _: User = Depends(require_manager),
):
    return (
        db.query(User)
        .filter(User.workspace_id == workspace.id)
        .order_by(User.created_at)
        .all()
    )


@router.post("/invite", response_model=UserResponse, status_code=201)
def invite_user(
    data: UserInvite,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    _: User = Depends(require_admin),
):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    if data.role not in ("admin", "manager", "sales"):
        raise HTTPException(status_code=400, detail="Função inválida")

    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
        is_admin=data.role == "admin",
        workspace_id=workspace.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    member_dict = jsonable_encoder(UserResponse.model_validate(user))
    background_tasks.add_task(realtime.broadcast_member_invited, workspace.id, member_dict)
    return user


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserRoleUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    current_user: User = Depends(require_admin),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Você não pode alterar seu próprio perfil aqui")

    user = db.query(User).filter(
        User.id == user_id,
        User.workspace_id == workspace.id,
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if data.role is not None:
        if data.role not in ("admin", "manager", "sales"):
            raise HTTPException(status_code=400, detail="Função inválida")
        user.role = data.role
        user.is_admin = data.role == "admin"
    if data.is_active is not None:
        user.is_active = data.is_active

    db.commit()
    db.refresh(user)
    member_dict = jsonable_encoder(UserResponse.model_validate(user))
    background_tasks.add_task(realtime.broadcast_member_updated, workspace.id, member_dict)
    return user


@router.delete("/users/{user_id}", status_code=204)
def remove_user(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    current_user: User = Depends(require_admin),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Você não pode remover a si mesmo")

    user = db.query(User).filter(
        User.id == user_id,
        User.workspace_id == workspace.id,
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    db.delete(user)
    db.commit()
    background_tasks.add_task(realtime.broadcast_member_removed, workspace.id, user_id)


# ── Integrations ──────────────────────────────────────────────────────────────

def _get_or_create_integrations(db: Session, workspace_id: int) -> WorkspaceIntegrations:
    record = db.query(WorkspaceIntegrations).filter(
        WorkspaceIntegrations.workspace_id == workspace_id
    ).first()
    if not record:
        record = WorkspaceIntegrations(workspace_id=workspace_id)
        db.add(record)
        db.commit()
        db.refresh(record)
    return record


@router.get("/integrations", response_model=WorkspaceIntegrationsResponse)
def get_integrations(
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    _: User = Depends(require_admin),
):
    return _get_or_create_integrations(db, workspace.id)


@router.put("/integrations", response_model=WorkspaceIntegrationsResponse)
def update_integrations(
    data: WorkspaceIntegrationsUpdate,
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    _: User = Depends(require_admin),
):
    record = _get_or_create_integrations(db, workspace.id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record
