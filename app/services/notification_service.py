from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.services.realtime import broadcast_notification


def create_notification(
    db: Session,
    workspace_id: int,
    type: str,
    title: str,
    message: str | None = None,
    user_id: int | None = None,
) -> Notification:
    notif = Notification(
        workspace_id=workspace_id,
        user_id=user_id,
        type=type,
        title=title,
        message=message,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    broadcast_notification(
        workspace_id,
        {
            "id": notif.id,
            "type": notif.type,
            "title": notif.title,
            "message": notif.message,
            "read": notif.read,
            "created_at": notif.created_at.isoformat(),
        },
        user_id=user_id,
    )
    return notif
