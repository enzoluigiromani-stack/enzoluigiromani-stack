import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.activity import Activity
from app.models.lead import Lead
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.activity import PaginatedActivities
from app.services.activity_service import serialize_activity
from app.services.permissions import require_sales
from app.services.workspace import require_workspace

router = APIRouter(tags=["activities"])


@router.get("/activities", response_model=PaginatedActivities)
def list_activities(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    query = (
        db.query(Activity)
        .filter(Activity.workspace_id == workspace.id)
    )
    if current_user.role == "sales":
        query = query.filter(Activity.user_id == current_user.id)

    total = query.count()
    items = (
        query.order_by(Activity.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return PaginatedActivities(
        items=[serialize_activity(a) for a in items],
        total=total,
        page=page,
        limit=limit,
        pages=math.ceil(total / limit) if total else 1,
    )


@router.get("/leads/{lead_id}/timeline", response_model=PaginatedActivities)
def lead_timeline(
    lead_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.workspace_id == workspace.id,
    ).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    query = db.query(Activity).filter(
        Activity.lead_id == lead_id,
        Activity.workspace_id == workspace.id,
    )
    total = query.count()
    items = (
        query.order_by(Activity.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return PaginatedActivities(
        items=[serialize_activity(a) for a in items],
        total=total,
        page=page,
        limit=limit,
        pages=math.ceil(total / limit) if total else 1,
    )
