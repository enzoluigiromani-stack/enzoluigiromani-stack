import logging
import os
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.lead_capture_event import LeadCaptureEvent
from app.models.workspace import Workspace
from app.schemas.lead import LeadResponse
from app.schemas.lead_capture_event import CaptureEventListResponse, LeadCaptureEventResponse
from app.api.leads import _upsert_lead
from app.services.activity_service import log_activity
from app.services.capture_parser import ParseError, parse
from app.services.notifications import notify_new_lead
from app.services.permissions import require_manager
from app.models.user import User
from app.services.workspace import require_workspace

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])

_SECRET = os.getenv("WEBHOOK_SECRET", "")


def _check_secret(x_webhook_secret: str | None):
    if _SECRET and x_webhook_secret != _SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")


# ── Endpoint principal de captura ─────────────────────────────────────────────

@router.post("/leads/{workspace_slug}", status_code=status.HTTP_200_OK)
def webhook_lead(
    workspace_slug: str,
    payload: Any,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    x_webhook_secret: str | None = Header(default=None),
):
    """
    Recebe payloads flexíveis de leads externos.

    Formatos suportados:
    - **Meta Lead Ads** — envelope `entry/changes/field_data`
    - **Formulários customizados** — dict plano com campos nomeados
    - **Landing pages** — `first_name` + `last_name` + UTMs

    Autenticação: header `X-Webhook-Secret` (quando `WEBHOOK_SECRET` está definido).
    """
    _check_secret(x_webhook_secret)

    workspace = db.query(Workspace).filter(Workspace.slug == workspace_slug).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")

    if not isinstance(payload, dict):
        raise HTTPException(status_code=422, detail="Payload deve ser um objeto JSON.")

    # 1. Persistir evento bruto antes de qualquer processamento
    event = LeadCaptureEvent(
        workspace_id=workspace.id,
        raw_payload=payload,
        source="unknown",
        processed=False,
    )
    db.add(event)
    db.flush()  # garante event.id antes do commit final

    try:
        # 2. Parser inteligente
        fields, source = parse(payload)
        event.source = source

        # 3. Garantir workspace_id no upsert
        fields["workspace_id"] = workspace.id

        # 4. Upsert do lead (anti-duplicação por email+workspace)
        lead, criado = _upsert_lead(db, fields["email"], workspace.id, fields)

        # 5. Vincular evento ao lead
        event.lead_id   = lead.id
        event.processed = True
        db.commit()

        # 6. Log de atividade
        log_activity(
            db,
            workspace_id=workspace.id,
            type="lead_created" if criado else "lead_updated",
            description=f"Lead {'capturado' if criado else 'atualizado'} via webhook ({source}): {lead.name}",
            lead_id=lead.id,
            meta={"source": source, "event_id": event.id},
        )

        # 7. Notificação em background (só para leads novos)
        if criado:
            background_tasks.add_task(notify_new_lead, lead)

        return {
            "status": "ok",
            "acao": "criado" if criado else "atualizado",
            "source": source,
            "event_id": event.id,
            "lead": jsonable_encoder(LeadResponse.model_validate(lead)),
        }

    except ParseError as exc:
        event.error = str(exc)
        db.commit()
        logger.warning("Webhook parse error (event=%s): %s", event.id, exc)
        raise HTTPException(status_code=422, detail=str(exc))

    except Exception as exc:
        event.error = f"Erro interno: {exc}"
        db.commit()
        logger.exception("Webhook error (event=%s)", event.id)
        raise HTTPException(status_code=500, detail="Erro ao processar lead.")


# ── Endpoint de listagem de eventos (auditoria) ───────────────────────────────

@router.get("/events", response_model=CaptureEventListResponse)
def list_capture_events(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    source: str | None = Query(None),
    processed: bool | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
    workspace: Workspace = Depends(require_workspace),
):
    """Lista eventos de captura brutos para auditoria (manager/admin)."""
    q = db.query(LeadCaptureEvent).filter(
        LeadCaptureEvent.workspace_id == workspace.id
    )
    if source is not None:
        q = q.filter(LeadCaptureEvent.source == source)
    if processed is not None:
        q = q.filter(LeadCaptureEvent.processed == processed)

    total = q.count()
    items = (
        q.order_by(LeadCaptureEvent.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return {"total": total, "items": items}


# ── Endpoint de detalhe do evento bruto ──────────────────────────────────────

@router.get("/events/{event_id}")
def get_capture_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
    workspace: Workspace = Depends(require_workspace),
):
    """Retorna o payload bruto de um evento de captura."""
    event = db.query(LeadCaptureEvent).filter(
        LeadCaptureEvent.id == event_id,
        LeadCaptureEvent.workspace_id == workspace.id,
    ).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return {
        "id":          event.id,
        "source":      event.source,
        "processed":   event.processed,
        "error":       event.error,
        "lead_id":     event.lead_id,
        "created_at":  event.created_at,
        "raw_payload": event.raw_payload,
    }
