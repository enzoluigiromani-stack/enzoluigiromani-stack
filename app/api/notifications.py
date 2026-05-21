from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.notification import NotificationResponse
from app.services.permissions import require_sales
from app.services.workspace import require_workspace

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=list[NotificationResponse])
def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    q = (
        db.query(Notification)
        .filter(
            Notification.workspace_id == workspace.id,
            Notification.user_id.in_([current_user.id, None]),
        )
        .order_by(Notification.created_at.desc())
    )
    if unread_only:
        q = q.filter(Notification.read == False)  # noqa: E712
    return q.limit(limit).all()


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    notif = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.workspace_id == workspace.id,
        )
        .first()
    )
    if not notif:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    notif.read = True
    db.commit()
    db.refresh(notif)
    return notif


@router.patch("/read-all", status_code=204)
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    (
        db.query(Notification)
        .filter(
            Notification.workspace_id == workspace.id,
            Notification.user_id.in_([current_user.id, None]),
            Notification.read == False,  # noqa: E712
        )
        .update({"read": True}, synchronize_session=False)
    )
    db.commit()
