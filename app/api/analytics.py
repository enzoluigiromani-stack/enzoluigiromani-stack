"""
Analytics API — endpoints thin; toda lógica fica no service.
Filtros compartilhados via Depends(AnalyticsFilterParams).
"""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.analytics import (
    BySourceResponse,
    ByUserResponse,
    ConversionFunnelResponse,
    LeadsByStageResponse,
    OverviewMetrics,
    RevenueResponse,
    TimelineResponse,
)
from app.services.analytics_service import AnalyticsService
from app.services.permissions import require_manager, require_sales
from app.services.workspace import require_workspace

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ── Shared filter dependency ──────────────────────────────────────────────────

class AnalyticsFilterParams:
    def __init__(
        self,
        date_from: Optional[date] = Query(None, description="Início do período (YYYY-MM-DD)"),
        date_to:   Optional[date] = Query(None, description="Fim do período (YYYY-MM-DD)"),
        user_id:   Optional[int]  = Query(None, description="Filtrar por usuário"),
        source:    Optional[str]  = Query(
            None,
            description="Filtrar por origem: meta_ads | instagram | whatsapp | google | referral | organic",
        ),
    ):
        self.date_from = date_from
        self.date_to   = date_to
        self.user_id   = user_id
        self.source    = source


def _svc(db: Session, workspace: Workspace) -> AnalyticsService:
    return AnalyticsService(db, workspace.id)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get(
    "/overview",
    response_model=OverviewMetrics,
    summary="Métricas gerais do workspace",
)
def get_overview(
    f: AnalyticsFilterParams = Depends(),
    db:        Session   = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    _: User = Depends(require_sales),
):
    return _svc(db, workspace).get_overview(f.date_from, f.date_to, f.user_id, f.source)


@router.get(
    "/leads-by-stage",
    response_model=LeadsByStageResponse,
    summary="Leads agrupados por etapa do pipeline",
)
def get_leads_by_stage(
    f: AnalyticsFilterParams = Depends(),
    db:        Session   = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    _: User = Depends(require_sales),
):
    return _svc(db, workspace).get_leads_by_stage(f.date_from, f.date_to, f.user_id, f.source)


@router.get(
    "/funnel",
    response_model=ConversionFunnelResponse,
    summary="Funil de conversão por etapa",
)
def get_funnel(
    f: AnalyticsFilterParams = Depends(),
    db:        Session   = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    _: User = Depends(require_sales),
):
    return _svc(db, workspace).get_funnel(f.date_from, f.date_to, f.user_id, f.source)


@router.get(
    "/revenue",
    response_model=RevenueResponse,
    summary="Receita estimada e fechada com breakdown mensal",
)
def get_revenue(
    f: AnalyticsFilterParams = Depends(),
    db:        Session   = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    _: User = Depends(require_sales),
):
    return _svc(db, workspace).get_revenue(f.date_from, f.date_to, f.user_id, f.source)


@router.get(
    "/by-user",
    response_model=ByUserResponse,
    summary="Performance por usuário (leads, conversões, receita, tarefas)",
)
def get_by_user(
    date_from: Optional[date] = Query(None),
    date_to:   Optional[date] = Query(None),
    db:        Session   = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    _: User = Depends(require_manager),
):
    return _svc(db, workspace).get_by_user(date_from, date_to)


@router.get(
    "/by-source",
    response_model=BySourceResponse,
    summary="Breakdown de leads e conversões por origem",
)
def get_by_source(
    date_from: Optional[date] = Query(None),
    date_to:   Optional[date] = Query(None),
    user_id:   Optional[int]  = Query(None),
    db:        Session   = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    _: User = Depends(require_sales),
):
    return _svc(db, workspace).get_by_source(date_from, date_to, user_id)


@router.get(
    "/timeline",
    response_model=TimelineResponse,
    summary="Série temporal de leads e receita (granularidade automática ou manual)",
)
def get_timeline(
    date_from:   Optional[date] = Query(None),
    date_to:     Optional[date] = Query(None),
    user_id:     Optional[int]  = Query(None),
    source:      Optional[str]  = Query(None),
    granularity: Optional[str]  = Query(
        None,
        description="day | week | month | auto (padrão)",
    ),
    db:        Session   = Depends(get_db),
    workspace: Workspace = Depends(require_workspace),
    _: User = Depends(require_sales),
):
    return _svc(db, workspace).get_timeline(date_from, date_to, user_id, source, granularity)
