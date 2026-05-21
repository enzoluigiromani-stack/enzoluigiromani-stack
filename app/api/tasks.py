import math
from datetime import datetime, timedelta
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.task import Task
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.task import PaginatedTasks, TaskCreate, TaskResponse, TaskUpdate
from app.services.activity_service import log_activity
from app.services.permissions import require_manager, require_sales
from app.services.task_service import (
    create_stale_reminders, serialize_task, sync_overdue,
)
from app.services.workspace import require_workspace
from app.services import realtime
from app.services.notification_service import create_notification

router = APIRouter(prefix="/tasks", tags=["tasks"])

_PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _build_query(
    db, workspace_id, user, status, priority,
    due_today, overdue_only, assigned_user_id,
    due_date_from=None, due_date_to=None, lead_id=None,
):
    query = db.query(Task).filter(Task.workspace_id == workspace_id)
    if user.role == "sales":
        query = query.filter(Task.assigned_user_id == user.id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if overdue_only:
        query = query.filter(Task.status == "overdue")
    if due_today:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(Task.due_date >= today, Task.due_date < today + timedelta(days=1))
    if due_date_from:
        query = query.filter(Task.due_date >= due_date_from)
    if due_date_to:
        query = query.filter(Task.due_date <= due_date_to)
    if assigned_user_id:
        query = query.filter(Task.assigned_user_id == assigned_user_id)
    if lead_id:
        query = query.filter(Task.lead_id == lead_id)
    return query


@router.get("/summary")
def task_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    """Contagens por status + tarefas vencendo hoje. Respeita isolamento por role."""
    sync_overdue(db, workspace.id)
    base = db.query(Task).filter(Task.workspace_id == workspace.id)
    if current_user.role == "sales":
        base = base.filter(Task.assigned_user_id == current_user.id)

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    return {
        "pending":   base.filter(Task.status == "pending").count(),
        "overdue":   base.filter(Task.status == "overdue").count(),
        "completed": base.filter(Task.status == "completed").count(),
        "due_today": base.filter(
            Task.due_date >= today,
            Task.due_date < today + timedelta(days=1),
            Task.status.in_(["pending", "overdue"]),
        ).count(),
    }


@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(
    data: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    task = Task(**data.model_dump(), workspace_id=workspace.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    log_activity(
        db, workspace_id=workspace.id, type="task_created",
        description=f"Tarefa criada: {task.title}",
        user_id=current_user.id, lead_id=task.lead_id,
        meta={"priority": task.priority, "due_date": str(task.due_date)},
    )
    background_tasks.add_task(realtime.broadcast_task_created, workspace.id, serialize_task(task).model_dump(mode="json"))
    background_tasks.add_task(
        create_notification, db, workspace.id,
        "task_created", f"Tarefa criada: {task.title}",
        f"Prioridade: {task.priority}",
        task.assigned_user_id,
    )
    return serialize_task(task)


@router.get("/my", response_model=PaginatedTasks)
def my_tasks(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    priority: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    sync_overdue(db, workspace.id)
    query = (
        db.query(Task)
        .filter(Task.workspace_id == workspace.id, Task.assigned_user_id == current_user.id)
    )
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    total = query.count()
    items = (
        query
        .order_by(Task.due_date.is_(None), Task.due_date.asc())
        .offset((page - 1) * limit).limit(limit).all()
    )
    return PaginatedTasks(
        items=[serialize_task(t) for t in items],
        total=total, page=page, limit=limit,
        pages=math.ceil(total / limit) if total else 1,
    )


@router.get("/", response_model=PaginatedTasks)
def list_tasks(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    priority: str = Query(None),
    due_today: bool = Query(False),
    overdue_only: bool = Query(False),
    assigned_user_id: int = Query(None),
    lead_id: int = Query(None),
    due_date_from: datetime = Query(None, description="ISO datetime — para filtro de calendário"),
    due_date_to: datetime = Query(None, description="ISO datetime — para filtro de calendário"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    sync_overdue(db, workspace.id)
    query = _build_query(
        db, workspace.id, current_user,
        status, priority, due_today, overdue_only, assigned_user_id,
        due_date_from=due_date_from, due_date_to=due_date_to, lead_id=lead_id,
    )
    total = query.count()
    items = (
        query
        .order_by(Task.due_date.is_(None), Task.due_date.asc())
        .offset((page - 1) * limit).limit(limit).all()
    )
    return PaginatedTasks(
        items=[serialize_task(t) for t in items],
        total=total, page=page, limit=limit,
        pages=math.ceil(total / limit) if total else 1,
    )


def _check_task_permission(task, current_user):
    if current_user.role == "sales" and task.assigned_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão para esta tarefa")


@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    task = db.query(Task).filter(Task.id == task_id, Task.workspace_id == workspace.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    _check_task_permission(task, current_user)
    task.status = "completed"
    task.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    log_activity(
        db, workspace_id=workspace.id, type="task_completed",
        description=f"Tarefa concluída: {task.title}",
        user_id=current_user.id, lead_id=task.lead_id,
        meta={"task_id": task.id},
    )
    background_tasks.add_task(realtime.broadcast_task_updated, workspace.id, serialize_task(task).model_dump(mode="json"))
    return serialize_task(task)


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    data: TaskUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    task = db.query(Task).filter(Task.id == task_id, Task.workspace_id == workspace.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    _check_task_permission(task, current_user)
    if data.status:
        task.status = data.status
        if data.status == "completed":
            task.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    background_tasks.add_task(realtime.broadcast_task_updated, workspace.id, serialize_task(task).model_dump(mode="json"))
    return serialize_task(task)


@router.post("/refresh")
def refresh_tasks(
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
    workspace: Workspace = Depends(require_workspace),
):
    """Sincroniza tarefas: marca overdue e cria lembretes para leads parados."""
    overdue = sync_overdue(db, workspace.id)
    reminders = create_stale_reminders(db, workspace.id)
    return {"overdue_updated": overdue, "reminders_created": reminders}
