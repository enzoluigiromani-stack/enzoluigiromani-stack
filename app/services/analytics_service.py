"""
Analytics Service — orquestra o repository e formata os responses.
Toda a lógica de negócio (cálculo de taxas, granularidade, labels) vive aqui.
O repository só sabe fazer queries; o service decide o que fazer com elas.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.analytics import AnalyticsRepository
from app.schemas.analytics import (
    BySourceResponse,
    ByUserResponse,
    ConversionFunnelResponse,
    FunnelStep,
    LeadsByStageResponse,
    MonthlyBreakdown,
    OverviewMetrics,
    RevenueResponse,
    SourceBreakdown,
    StageMetrics,
    TimelinePoint,
    TimelineResponse,
    UserPerformance,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _period_label(date_from: Optional[date], date_to: Optional[date]) -> str:
    fmt = "%d/%m/%Y"
    if date_from and date_to:
        return f"{date_from.strftime(fmt)} – {date_to.strftime(fmt)}"
    if date_from:
        return f"A partir de {date_from.strftime(fmt)}"
    if date_to:
        return f"Até {date_to.strftime(fmt)}"
    return "Todos os períodos"


def _auto_granularity(date_from: Optional[date], date_to: Optional[date]) -> str:
    if not date_from or not date_to:
        return "month"
    delta = (date_to - date_from).days
    if delta <= 31:
        return "day"
    if delta <= 90:
        return "week"
    return "month"


def _safe_pct(numerator: int | float, denominator: int | float) -> float:
    if not denominator:
        return 0.0
    return round(numerator / denominator * 100, 2)


# ── Service class ─────────────────────────────────────────────────────────────

class AnalyticsService:
    def __init__(self, db: Session, workspace_id: int):
        self.repo = AnalyticsRepository(db, workspace_id)

    # ── Overview ──────────────────────────────────────────────────────────────

    def get_overview(
        self,
        date_from: Optional[date] = None,
        date_to:   Optional[date] = None,
        user_id:   Optional[int]  = None,
        source:    Optional[str]  = None,
    ) -> OverviewMetrics:
        kw = dict(date_from=date_from, date_to=date_to, user_id=user_id, source=source)

        total     = self.repo.count_leads(**kw)
        converted = self.repo.count_closed(**kw)
        lost      = self.repo.count_lost(**kw)
        active    = max(total - converted - lost, 0)

        closed_rev = self.repo.sum_budget(closed_only=True, **kw)
        est_rev    = self.repo.sum_budget(active_only=True, **kw)
        tasks      = self.repo.task_summary(user_id=user_id)
        convs      = self.repo.count_open_conversations()

        return OverviewMetrics(
            period_label=        _period_label(date_from, date_to),
            total_leads=         total,
            new_leads=           total,
            active_leads=        active,
            converted_leads=     converted,
            lost_leads=          lost,
            conversion_rate=     _safe_pct(converted, total),
            lost_rate=           _safe_pct(lost, total),
            closed_revenue=      closed_rev,
            estimated_revenue=   est_rev,
            total_pipeline_value= closed_rev + est_rev,
            avg_deal_size=       round(closed_rev / converted, 2) if converted else 0.0,
            tasks_completed=     tasks["completed"],
            tasks_pending=       tasks["pending"],
            tasks_overdue=       tasks["overdue"],
            open_conversations=  convs,
        )

    # ── Leads by Stage ────────────────────────────────────────────────────────

    def get_leads_by_stage(
        self,
        date_from: Optional[date] = None,
        date_to:   Optional[date] = None,
        user_id:   Optional[int]  = None,
        source:    Optional[str]  = None,
    ) -> LeadsByStageResponse:
        rows, no_stage = self.repo.leads_by_stage(date_from, date_to, user_id, source)
        total = sum(r["lead_count"] for r in rows) + no_stage

        stages = []
        prev_count: Optional[int] = None
        for r in rows:
            conv_prev = (
                _safe_pct(r["lead_count"], prev_count)
                if prev_count is not None else None
            )
            stages.append(StageMetrics(
                stage_id=             r["stage_id"],
                stage_name=           r["stage_name"],
                stage_color=          r["stage_color"],
                stage_order=          r["stage_order"],
                lead_count=           r["lead_count"],
                total_budget=         round(r["total_budget"], 2),
                avg_budget=           round(r["avg_budget"], 2),
                pct_of_total=         _safe_pct(r["lead_count"], total),
                conversion_from_prev= conv_prev,
            ))
            prev_count = r["lead_count"]

        return LeadsByStageResponse(
            stages=         stages,
            no_stage_count= no_stage,
            total_leads=    total,
            period_label=   _period_label(date_from, date_to),
        )

    # ── Conversion Funnel ─────────────────────────────────────────────────────

    def get_funnel(
        self,
        date_from: Optional[date] = None,
        date_to:   Optional[date] = None,
        user_id:   Optional[int]  = None,
        source:    Optional[str]  = None,
    ) -> ConversionFunnelResponse:
        rows, _ = self.repo.leads_by_stage(date_from, date_to, user_id, source)
        if not rows:
            return ConversionFunnelResponse(steps=[], overall_conversion_rate=0.0)

        first_count = rows[0]["lead_count"] if rows else 1
        last_closed = rows[-1]["lead_count"] if rows else 0

        steps = []
        prev_count: Optional[int] = None
        for r in rows:
            steps.append(FunnelStep(
                stage_id=             r["stage_id"],
                stage_name=           r["stage_name"],
                stage_color=          r["stage_color"],
                stage_order=          r["stage_order"],
                lead_count=           r["lead_count"],
                entered_pct=          _safe_pct(r["lead_count"], first_count),
                converted_from_prev=  (
                    _safe_pct(r["lead_count"], prev_count)
                    if prev_count is not None else None
                ),
            ))
            prev_count = r["lead_count"]

        return ConversionFunnelResponse(
            steps=steps,
            overall_conversion_rate=_safe_pct(last_closed, first_count),
        )

    # ── Revenue ───────────────────────────────────────────────────────────────

    def get_revenue(
        self,
        date_from: Optional[date] = None,
        date_to:   Optional[date] = None,
        user_id:   Optional[int]  = None,
        source:    Optional[str]  = None,
    ) -> RevenueResponse:
        kw = dict(date_from=date_from, date_to=date_to, user_id=user_id, source=source)

        closed_count = self.repo.count_closed(**kw)
        open_count   = self.repo.count_active(**kw)
        closed_rev   = self.repo.sum_budget(closed_only=True, **kw)
        est_rev      = self.repo.sum_budget(active_only=True, **kw)

        monthly_raw = self.repo.monthly_breakdown(date_from, date_to, user_id, source)
        monthly = [
            MonthlyBreakdown(
                period=         r["period"],
                new_leads=      r["new_leads"],
                closed_leads=   r["closed_leads"],
                closed_revenue= round(r["closed_revenue"], 2),
                avg_deal_size=  round(r["avg_deal_size"], 2),
            )
            for r in monthly_raw
        ]

        return RevenueResponse(
            closed_revenue=       round(closed_rev, 2),
            estimated_revenue=    round(est_rev, 2),
            total_pipeline_value= round(closed_rev + est_rev, 2),
            avg_deal_value=       round(closed_rev / closed_count, 2) if closed_count else 0.0,
            total_deals_closed=   closed_count,
            total_deals_open=     open_count,
            monthly=              monthly,
            period_label=         _period_label(date_from, date_to),
        )

    # ── By User ───────────────────────────────────────────────────────────────

    def get_by_user(
        self,
        date_from: Optional[date] = None,
        date_to:   Optional[date] = None,
    ) -> ByUserResponse:
        rows = self.repo.user_metrics(date_from, date_to)
        users = [
            UserPerformance(
                user_id=           r["user_id"],
                user_name=         r["user_name"],
                user_email=        r["user_email"],
                leads_assigned=    r["leads_assigned"],
                leads_converted=   r["leads_converted"],
                leads_lost=        r["leads_lost"],
                leads_active=      r["leads_active"],
                conversion_rate=   round(r["conversion_rate"], 2),
                closed_revenue=    round(r["closed_revenue"], 2),
                estimated_revenue= round(r["estimated_revenue"], 2),
                avg_deal_size=     round(r["avg_deal_size"], 2),
                tasks_completed=   r["tasks_completed"],
                tasks_pending=     r["tasks_pending"],
                tasks_overdue=     r["tasks_overdue"],
            )
            for r in rows
        ]
        return ByUserResponse(
            users=        users,
            period_label= _period_label(date_from, date_to),
        )

    # ── By Source ─────────────────────────────────────────────────────────────

    def get_by_source(
        self,
        date_from: Optional[date] = None,
        date_to:   Optional[date] = None,
        user_id:   Optional[int]  = None,
    ) -> BySourceResponse:
        rows, total = self.repo.source_breakdown(date_from, date_to, user_id)
        sources = [
            SourceBreakdown(
                source_key=      r["source_key"],
                source_label=    r["source_label"],
                lead_count=      r["lead_count"],
                converted_count= r["converted_count"],
                lost_count=      r["lost_count"],
                active_count=    r["active_count"],
                conversion_rate= round(r["conversion_rate"], 2),
                total_budget=    round(r["total_budget"], 2),
                avg_budget=      round(r["avg_budget"], 2),
                pct_of_total=    _safe_pct(r["lead_count"], total),
            )
            for r in rows
        ]
        return BySourceResponse(
            sources=      sources,
            total_leads=  total,
            period_label= _period_label(date_from, date_to),
        )

    # ── Timeline ──────────────────────────────────────────────────────────────

    def get_timeline(
        self,
        date_from:   Optional[date] = None,
        date_to:     Optional[date] = None,
        user_id:     Optional[int]  = None,
        source:      Optional[str]  = None,
        granularity: Optional[str]  = None,
    ) -> TimelineResponse:
        # Default period: last 6 months when no filter given
        effective_from = date_from
        effective_to   = date_to
        if not effective_from and not effective_to:
            effective_to   = date.today()
            effective_from = effective_to - timedelta(days=180)

        gran = granularity or _auto_granularity(effective_from, effective_to)

        raw = self.repo.timeline(effective_from, effective_to, user_id, source, gran)
        points = [
            TimelinePoint(
                period=          r["period"],
                new_leads=       r["new_leads"],
                converted_leads= r["converted_leads"],
                closed_revenue=  round(r["closed_revenue"], 2),
            )
            for r in raw
        ]

        return TimelineResponse(
            points=          points,
            granularity=     gran,
            total_new=       sum(p.new_leads for p in points),
            total_converted= sum(p.converted_leads for p in points),
            total_revenue=   round(sum(p.closed_revenue for p in points), 2),
            period_label=    _period_label(effective_from, effective_to),
        )
