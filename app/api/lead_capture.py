"""
Endpoints de Lead Capture — auditoria, estatísticas e testes.

GET  /lead-capture/events          Lista eventos de captura (paginado, filtros)
GET  /lead-capture/events/{id}     Payload bruto de um evento
GET  /lead-capture/stats           Estatísticas por fonte/status
POST /lead-capture/meta/test       Simula um webhook Meta Lead Ads
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.lead_capture_event import LeadCaptureEvent
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.lead import LeadResponse
from app.schemas.lead_capture_event import CaptureEventListResponse
from app.services.activity_service import log_activity
from app.services.capture_parser import ParseError, parse
from app.services.notifications import notify_new_lead
from app.services.permissions import require_manager
from app.services.platform_adapters.meta import MetaLeadAdsAdapter
from app.services.tag_service import compute_tags, merge_tags
from app.services.workspace import require_workspace
from app.api.leads import _upsert_lead
from app.services import realtime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/lead-capture", tags=["lead-capture"])

_meta_adapter = MetaLeadAdsAdapter()


# ── Schemas de entrada ────────────────────────────────────────────────────────

class MetaTestPayload(BaseModel):
    workspace_slug: str
    name: str
    email: str
    phone: str | None = None
    leadgen_id: str = "test_000"
    campaign_name: str | None = None
    adset_name: str | None = None
    ad_name: str | None = None
    utm_campaign: str | None = None
    utm_medium: str | None = None
    utm_content: str | None = None
    utm_term: str | None = None
    budget: float | None = None


# ── Listagem de eventos ───────────────────────────────────────────────────────

@router.get("/events", response_model=CaptureEventListResponse)
def list_events(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    source: str | None = Query(None, description="Filtrar por plataforma (meta_lead_ads, custom, ...)"),
    processed: bool | None = Query(None),
    since: datetime | None = Query(None, description="ISO 8601 — eventos a partir desta data"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
    workspace: Workspace = Depends(require_workspace),
):
    """Lista eventos de captura brutos com filtros (manager+)."""
    q = db.query(LeadCaptureEvent).filter(
        LeadCaptureEvent.workspace_id == workspace.id
    )
    if source:
        q = q.filter(LeadCaptureEvent.source == source)
    if processed is not None:
        q = q.filter(LeadCaptureEvent.processed == processed)
    if since:
        q = q.filter(LeadCaptureEvent.created_at >= since)

    total = q.count()
    items = (
        q.order_by(LeadCaptureEvent.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return {"total": total, "items": items}


@router.get("/events/{event_id}")
def get_event(
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


# ── Estatísticas ──────────────────────────────────────────────────────────────

@router.get("/stats")
def capture_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
    workspace: Workspace = Depends(require_workspace),
):
    """Resumo de eventos por fonte e status."""
    rows = (
        db.query(
            LeadCaptureEvent.source,
            LeadCaptureEvent.processed,
            func.count(LeadCaptureEvent.id).label("count"),
        )
        .filter(LeadCaptureEvent.workspace_id == workspace.id)
        .group_by(LeadCaptureEvent.source, LeadCaptureEvent.processed)
        .all()
    )

    by_source: dict[str, dict] = {}
    total_ok = total_err = 0
    for source, processed, count in rows:
        if source not in by_source:
            by_source[source] = {"processed": 0, "failed": 0, "total": 0}
        if processed:
            by_source[source]["processed"] += count
            total_ok += count
        else:
            by_source[source]["failed"] += count
            total_err += count
        by_source[source]["total"] += count

    return {
        "total":      total_ok + total_err,
        "processed":  total_ok,
        "failed":     total_err,
        "by_source":  by_source,
    }


# ── Teste de webhook Meta ─────────────────────────────────────────────────────

@router.post("/meta/test", status_code=200)
def meta_test(
    body: MetaTestPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """
    Simula um webhook Meta Lead Ads para testar a integração.
    Requer papel manager ou admin.
    """
    workspace = db.query(Workspace).filter(
        Workspace.slug == body.workspace_slug
    ).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")

    if workspace.id != current_user.workspace_id:
        raise HTTPException(status_code=403, detail="Acesso negado a este workspace.")

    extra: dict[str, Any] = {}
    if body.utm_medium:  extra["utm_medium"]  = body.utm_medium
    if body.utm_content: extra["utm_content"]  = body.utm_content
    if body.utm_term:    extra["utm_term"]     = body.utm_term

    envelope = _meta_adapter.build_test_envelope(
        name          = body.name,
        email         = body.email,
        phone         = body.phone,
        leadgen_id    = body.leadgen_id,
        campaign_name = body.campaign_name,
        adset_name    = body.adset_name,
        ad_name       = body.ad_name,
        utm_campaign  = body.utm_campaign,
        **extra,
    )

    # Reutiliza a lógica central de captura
    event = LeadCaptureEvent(
        workspace_id=workspace.id,
        raw_payload=envelope,
        source="meta_lead_ads",
        processed=False,
    )
    db.add(event)
    db.flush()

    try:
        fields, source = parse(envelope)
        fields["workspace_id"] = workspace.id
        if body.budget:
            fields["budget"] = body.budget

        tags = compute_tags(fields)
        if tags:
            fields["tags"] = tags

        lead, criado = _upsert_lead(db, fields["email"], workspace.id, fields)
        event.lead_id   = lead.id
        event.processed = True
        db.commit()

        log_activity(
            db,
            workspace_id=workspace.id,
            type="lead_captured" if criado else "lead_updated_from_webhook",
            description=(
                f"[TESTE Meta] Lead {'capturado' if criado else 'atualizado'}: {lead.name}"
            ),
            user_id=current_user.id,
            lead_id=lead.id,
            meta={"source": source, "event_id": event.id, "test": True, "tags": tags},
        )

        lead_dict = jsonable_encoder(LeadResponse.model_validate(lead))
        if criado:
            background_tasks.add_task(notify_new_lead, lead)
            background_tasks.add_task(realtime.broadcast_lead_created, workspace.id, lead_dict)
        else:
            background_tasks.add_task(realtime.broadcast_lead_updated, workspace.id, lead_dict)

        return {
            "status":   "ok",
            "acao":     "criado" if criado else "atualizado",
            "source":   source,
            "tags":     tags,
            "event_id": event.id,
            "lead":     jsonable_encoder(LeadResponse.model_validate(lead)),
            "envelope": envelope,
        }

    except ParseError as exc:
        event.error = str(exc)
        db.commit()
        raise HTTPException(status_code=422, detail=str(exc))
