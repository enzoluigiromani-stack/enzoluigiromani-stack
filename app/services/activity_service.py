import logging
from typing import Any
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.schemas.activity import ActivityResponse

# Tipos válidos de atividade
ACTIVITY_TYPES = {
    "lead_created",
    "lead_updated",
    "lead_moved",
    "email_sent",
    "whatsapp_sent",
    "user_login",
    "stage_created",
    "task_created",
    "task_completed",
    "followup_created",
}


def log_activity(
    db: Session,
    *,
    workspace_id: int,
    type: str,
    description: str,
    user_id: int | None = None,
    lead_id: int | None = None,
    meta: dict | None = None,
) -> None:
    """Registra uma atividade de auditoria. Falhas são absorvidas para não quebrar o fluxo principal."""
    try:
        db.add(Activity(
            workspace_id=workspace_id,
            user_id=user_id,
            lead_id=lead_id,
            type=type,
            description=description,
            meta=meta,
        ))
        db.commit()
    except Exception as exc:
        db.rollback()
        logging.warning("log_activity falhou [%s]: %s", type, exc)


def serialize_activity(a: Activity) -> ActivityResponse:
    return ActivityResponse(
        id=a.id,
        type=a.type,
        description=a.description,
        meta=a.meta,
        lead_id=a.lead_id,
        user_id=a.user_id,
        user_name=a.user.name if a.user else None,
        created_at=a.created_at,
    )
