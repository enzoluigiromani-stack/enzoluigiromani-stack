from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.lead import Lead
from app.schemas.task import TaskResponse


def serialize_task(t: Task) -> TaskResponse:
    return TaskResponse(
        id=t.id,
        workspace_id=t.workspace_id,
        lead_id=t.lead_id,
        assigned_user_id=t.assigned_user_id,
        title=t.title,
        description=t.description,
        status=t.status,
        priority=t.priority,
        due_date=t.due_date,
        completed_at=t.completed_at,
        created_at=t.created_at,
        lead_name=t.lead.name if t.lead else None,
        assigned_user_name=t.assigned_user.name if t.assigned_user else None,
    )


def sync_overdue(db: Session, workspace_id: int) -> int:
    """Marca como overdue todas as tarefas pending com due_date vencida."""
    updated = (
        db.query(Task)
        .filter(
            Task.workspace_id == workspace_id,
            Task.status == "pending",
            Task.due_date.isnot(None),
            Task.due_date < datetime.utcnow(),
        )
        .update({"status": "overdue"}, synchronize_session=False)
    )
    db.commit()
    return updated


def create_stale_reminders(db: Session, workspace_id: int, stale_days: int = 7) -> int:
    """Cria lembrete para leads sem movimentação há mais de stale_days dias."""
    cutoff = datetime.utcnow() - timedelta(days=stale_days)
    stale_leads = (
        db.query(Lead)
        .filter(
            Lead.workspace_id == workspace_id,
            Lead.updated_at.isnot(None),
            Lead.updated_at < cutoff,
            Lead.status.notin_(["fechado", "perdido"]),
        )
        .all()
    )
    created = 0
    for lead in stale_leads:
        existing = (
            db.query(Task)
            .filter(
                Task.workspace_id == workspace_id,
                Task.lead_id == lead.id,
                Task.status.in_(["pending", "overdue"]),
                Task.title.like("Lembrete:%"),
            )
            .first()
        )
        if not existing:
            db.add(Task(
                workspace_id=workspace_id,
                lead_id=lead.id,
                assigned_user_id=lead.user_id,
                title=f"Lembrete: {lead.name} parado há {stale_days}+ dias",
                description=(
                    f"Lead sem movimentação desde "
                    f"{lead.updated_at.strftime('%d/%m/%Y')}."
                ),
                priority="medium",
                due_date=datetime.utcnow() + timedelta(days=1),
            ))
            created += 1
    if created:
        db.commit()
    return created


def create_followup_task(db: Session, workspace_id: int, lead, stage_name: str) -> Task:
    """Cria follow-up automático quando lead entra em determinada etapa."""
    task = Task(
        workspace_id=workspace_id,
        lead_id=lead.id,
        assigned_user_id=lead.user_id,
        title=f"Follow-up: {lead.name}",
        description=f"Lead entrou em '{stage_name}'. Realizar follow-up.",
        priority="high",
        due_date=datetime.utcnow() + timedelta(days=1),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
