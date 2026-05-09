import re
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.pipeline_stage import PipelineStage
from app.models.workspace import Workspace

_DEFAULT_STAGES = [
    {"name": "novo",        "order": 1, "color": "#6366f1"},
    {"name": "contato",     "order": 2, "color": "#f59e0b"},
    {"name": "qualificado", "order": 3, "color": "#3b82f6"},
    {"name": "proposta",    "order": 4, "color": "#8b5cf6"},
    {"name": "fechado",     "order": 5, "color": "#22c55e"},
    {"name": "perdido",     "order": 6, "color": "#ef4444"},
]


def _slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    return re.sub(r"^-+|-+$", "", slug)


def _unique_slug(db: Session, base: str) -> str:
    slug = _slugify(base)
    candidate, counter = slug, 1
    while db.query(Workspace).filter(Workspace.slug == candidate).first():
        candidate = f"{slug}-{counter}"
        counter += 1
    return candidate


def create_workspace(db: Session, name: str) -> Workspace:
    """Cria workspace + stages padrão. Usa flush — o chamador deve commitar."""
    slug = _unique_slug(db, name)
    workspace = Workspace(name=name, slug=slug)
    db.add(workspace)
    db.flush()
    for stage_data in _DEFAULT_STAGES:
        db.add(PipelineStage(**stage_data, workspace_id=workspace.id))
    db.flush()
    return workspace


# Import tardio para evitar circular (services.auth não importa services.workspace)
from app.services.auth import get_current_user  # noqa: E402
from app.models.user import User                # noqa: E402


def require_workspace(current_user: User = Depends(get_current_user)) -> Workspace:
    """Dependency FastAPI: retorna o Workspace do usuário autenticado."""
    if not current_user.workspace:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário sem workspace associado",
        )
    return current_user.workspace
