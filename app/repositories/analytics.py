"""
Analytics Repository — camada de acesso a dados.
Todas as queries SQLAlchemy ficam aqui; sem lógica de negócio.
Preparado para futura migração para PostgreSQL (evita SQLite-only funções).
"""
from __future__ import annotations

from datetime import date, datetime, time
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.lead import Lead
from app.models.pipeline_stage import PipelineStage
from app.models.task import Task
from app.models.user import User


# ── Source classification helpers ────────────────────────────────────────────

def _src_meta():
    return or_(
        Lead.utm_source.ilike("facebook"),
        Lead.utm_source.ilike("meta"),
        Lead.utm_source.ilike("fb"),
        Lead.source.ilike("meta%"),
        Lead.source.ilike("meta_lead%"),
    )

def _src_instagram():
    return or_(
        Lead.utm_source.ilike("instagram"),
        Lead.source.ilike("instagram"),
    )

def _src_whatsapp():
    return or_(
        Lead.source.ilike("whatsapp"),
        Lead.utm_medium.ilike("whatsapp"),
    )

def _src_google():
    return or_(
        Lead.utm_source.ilike("google%"),
        Lead.source.ilike("google%"),
    )

def _src_referral():
    return or_(
        Lead.utm_source.ilike("referral"),
        Lead.utm_medium.ilike("referral"),
        Lead.source.ilike("referral"),
        Lead.source.ilike("indica%"),
    )

def _src_organic():
    return and_(
        Lead.utm_source.is_(None),
        Lead.utm_medium.is_(None),
        or_(Lead.source.is_(None), Lead.source == ""),
    )


SOURCE_CATALOGUE = [
    ("meta_ads",   "Meta Ads",  _src_meta),
    ("instagram",  "Instagram", _src_instagram),
    ("whatsapp",   "WhatsApp",  _src_whatsapp),
    ("google",     "Google",    _src_google),
    ("referral",   "Indicação", _src_referral),
    ("organic",    "Orgânico",  _src_organic),
]


def _source_expr(source_key: str):
    """Return a SQLAlchemy filter expression for a named source key."""
    mapping = {k: fn for k, _, fn in SOURCE_CATALOGUE}
    factory = mapping.get(source_key)
    return factory() if factory else None


# ── Stage outcome helpers ─────────────────────────────────────────────────────

def _closed_expr():
    return or_(
        func.lower(PipelineStage.name).contains("fech"),
        func.lower(Lead.status) == "fechado",
    )

def _lost_expr():
    return or_(
        func.lower(PipelineStage.name).contains("perd"),
        func.lower(Lead.status) == "perdido",
    )

def _active_expr():
    return and_(~_closed_expr(), ~_lost_expr())


# ── Repository class ──────────────────────────────────────────────────────────

class AnalyticsRepository:
    """
    All queries are workspace-scoped.
    Accepts optional date_from / date_to / user_id / source filters.
    """

    def __init__(self, db: Session, workspace_id: int):
        self.db = db
        self.workspace_id = workspace_id

    # ── Base queries ─────────────────────────────────────────────────────────

    def _leads(
        self,
        date_from: Optional[date] = None,
        date_to:   Optional[date] = None,
        user_id:   Optional[int]  = None,
        source:    Optional[str]  = None,
    ):
        q = self.db.query(Lead).filter(Lead.workspace_id == self.workspace_id)
        if date_from:
            q = q.filter(Lead.created_at >= datetime.combine(date_from, time.min))
        if date_to:
            q = q.filter(Lead.created_at <= datetime.combine(date_to, time.max))
        if user_id:
            q = q.filter(Lead.user_id == user_id)
        if source:
            expr = _source_expr(source)
            if expr is not None:
                q = q.filter(expr)
        return q

    def _leads_with_stage(
        self,
        date_from: Optional[date] = None,
        date_to:   Optional[date] = None,
        user_id:   Optional[int]  = None,
        source:    Optional[str]  = None,
    ):
        return (
            self._leads(date_from, date_to, user_id, source)
            .outerjoin(PipelineStage, Lead.stage_id == PipelineStage.id)
        )

    def _tasks(self, user_id: Optional[int] = None):
        q = self.db.query(Task).filter(Task.workspace_id == self.workspace_id)
        if user_id:
            q = q.filter(Task.assigned_user_id == user_id)
        return q

    # ── Overview counts ──────────────────────────────────────────────────────

    def count_leads(self, **kw) -> int:
        return self._leads(**kw).count()

    def count_closed(self, **kw) -> int:
        return self._leads_with_stage(**kw).filter(_closed_expr()).count()

    def count_lost(self, **kw) -> int:
        return self._leads_with_stage(**kw).filter(_lost_expr()).count()

    def count_active(self, **kw) -> int:
        return self._leads_with_stage(**kw).filter(_active_expr()).count()

    def sum_budget(self, closed_only: bool = False, active_only: bool = False, **kw) -> float:
        q = self._leads_with_stage(**kw)
        if closed_only:
            q = q.filter(_closed_expr())
        elif active_only:
            q = q.filter(_active_expr())
        result = q.with_entities(func.coalesce(func.sum(Lead.budget), 0.0)).scalar()
        return float(result or 0)

    # ── Task summary ─────────────────────────────────────────────────────────

    def task_summary(self, user_id: Optional[int] = None) -> Dict[str, int]:
        q = self._tasks(user_id)
        return {
            "completed": q.filter(Task.status == "completed").count(),
            "pending":   q.filter(Task.status == "pending").count(),
            "overdue":   q.filter(Task.status == "overdue").count(),
        }

    # ── Conversations ────────────────────────────────────────────────────────

    def count_open_conversations(self) -> int:
        return (
            self.db.query(Conversation)
            .filter(
                Conversation.workspace_id == self.workspace_id,
                Conversation.status == "open",
            )
            .count()
        )

    # ── Leads by stage ───────────────────────────────────────────────────────

    def leads_by_stage(
        self,
        date_from: Optional[date] = None,
        date_to:   Optional[date] = None,
        user_id:   Optional[int]  = None,
        source:    Optional[str]  = None,
    ) -> Tuple[List[Dict], int]:
        """Returns (list_of_stage_dicts, no_stage_count)."""
        base = self._leads(date_from, date_to, user_id, source)
        stages = (
            self.db.query(PipelineStage)
            .filter(PipelineStage.workspace_id == self.workspace_id)
            .order_by(PipelineStage.order)
            .all()
        )

        rows = []
        for stage in stages:
            q = base.filter(Lead.stage_id == stage.id)
            count = q.count()
            budget_sum = float(
                q.with_entities(func.coalesce(func.sum(Lead.budget), 0.0)).scalar() or 0
            )
            rows.append({
                "stage_id":    stage.id,
                "stage_name":  stage.name,
                "stage_color": stage.color,
                "stage_order": stage.order,
                "lead_count":  count,
                "total_budget": budget_sum,
                "avg_budget":   budget_sum / count if count else 0.0,
            })

        no_stage = base.filter(Lead.stage_id.is_(None)).count()
        return rows, no_stage

    # ── Monthly breakdown ────────────────────────────────────────────────────

    def monthly_breakdown(
        self,
        date_from: Optional[date] = None,
        date_to:   Optional[date] = None,
        user_id:   Optional[int]  = None,
        source:    Optional[str]  = None,
    ) -> List[Dict]:
        period_expr = func.strftime("%Y-%m", Lead.created_at)

        # All leads per month
        new_rows = (
            self._leads(date_from, date_to, user_id, source)
            .with_entities(
                period_expr.label("period"),
                func.count(Lead.id).label("new_leads"),
            )
            .group_by(period_expr)
            .all()
        )

        # Closed leads per month
        closed_rows = (
            self._leads_with_stage(date_from, date_to, user_id, source)
            .filter(_closed_expr())
            .with_entities(
                period_expr.label("period"),
                func.count(Lead.id).label("closed_leads"),
                func.coalesce(func.sum(Lead.budget), 0.0).label("closed_rev"),
            )
            .group_by(period_expr)
            .all()
        )

        closed_map = {r.period: r for r in closed_rows}
        result = []
        for r in new_rows:
            c = closed_map.get(r.period)
            cl = c.closed_leads if c else 0
            cr = float(c.closed_rev if c else 0)
            result.append({
                "period":         r.period,
                "new_leads":      r.new_leads,
                "closed_leads":   cl,
                "closed_revenue": cr,
                "avg_deal_size":  cr / cl if cl else 0.0,
            })

        return sorted(result, key=lambda x: x["period"])

    # ── Timeline ─────────────────────────────────────────────────────────────

    def timeline(
        self,
        date_from:   Optional[date] = None,
        date_to:     Optional[date] = None,
        user_id:     Optional[int]  = None,
        source:      Optional[str]  = None,
        granularity: str = "month",
    ) -> List[Dict]:
        fmt_map = {"day": "%Y-%m-%d", "week": "%Y-%W", "month": "%Y-%m"}
        fmt = fmt_map.get(granularity, "%Y-%m")
        period_expr = func.strftime(fmt, Lead.created_at)

        new_rows = (
            self._leads(date_from, date_to, user_id, source)
            .with_entities(
                period_expr.label("period"),
                func.count(Lead.id).label("new_leads"),
            )
            .group_by(period_expr)
            .all()
        )

        closed_rows = (
            self._leads_with_stage(date_from, date_to, user_id, source)
            .filter(_closed_expr())
            .with_entities(
                period_expr.label("period"),
                func.count(Lead.id).label("closed_count"),
                func.coalesce(func.sum(Lead.budget), 0.0).label("revenue"),
            )
            .group_by(period_expr)
            .all()
        )

        closed_map = {r.period: r for r in closed_rows}
        result = []
        for r in new_rows:
            c = closed_map.get(r.period)
            result.append({
                "period":          r.period,
                "new_leads":       r.new_leads,
                "converted_leads": c.closed_count if c else 0,
                "closed_revenue":  float(c.revenue if c else 0),
            })

        return sorted(result, key=lambda x: x["period"])

    # ── By user ──────────────────────────────────────────────────────────────

    def user_metrics(
        self,
        date_from: Optional[date] = None,
        date_to:   Optional[date] = None,
    ) -> List[Dict]:
        users = (
            self.db.query(User)
            .filter(User.workspace_id == self.workspace_id, User.is_active == True)
            .order_by(User.name)
            .all()
        )

        rows = []
        for user in users:
            kw = dict(date_from=date_from, date_to=date_to, user_id=user.id)

            total     = self.count_leads(**kw)
            converted = self.count_closed(**kw)
            lost      = self.count_lost(**kw)
            active    = total - converted - lost

            closed_rev = self.sum_budget(closed_only=True, **kw)
            est_rev    = self.sum_budget(active_only=True, **kw)

            tasks = self.task_summary(user_id=user.id)

            rows.append({
                "user_id":           user.id,
                "user_name":         user.name,
                "user_email":        user.email,
                "leads_assigned":    total,
                "leads_converted":   converted,
                "leads_lost":        lost,
                "leads_active":      max(active, 0),
                "conversion_rate":   (converted / total * 100) if total else 0.0,
                "closed_revenue":    closed_rev,
                "estimated_revenue": est_rev,
                "avg_deal_size":     (closed_rev / converted) if converted else 0.0,
                "tasks_completed":   tasks["completed"],
                "tasks_pending":     tasks["pending"],
                "tasks_overdue":     tasks["overdue"],
            })

        return rows

    # ── By source ────────────────────────────────────────────────────────────

    def source_breakdown(
        self,
        date_from: Optional[date] = None,
        date_to:   Optional[date] = None,
        user_id:   Optional[int]  = None,
    ) -> Tuple[List[Dict], int]:
        """Returns (list_of_source_dicts, total_leads_in_period)."""
        total = self.count_leads(date_from=date_from, date_to=date_to, user_id=user_id)

        rows = []
        for key, label, expr_fn in SOURCE_CATALOGUE:
            expr = expr_fn()
            base    = self._leads(date_from, date_to, user_id).filter(expr)
            joined  = self._leads_with_stage(date_from, date_to, user_id).filter(expr)

            count     = base.count()
            converted = joined.filter(_closed_expr()).count()
            lost      = joined.filter(_lost_expr()).count()
            budget    = float(base.with_entities(
                func.coalesce(func.sum(Lead.budget), 0.0)
            ).scalar() or 0)

            rows.append({
                "source_key":      key,
                "source_label":    label,
                "lead_count":      count,
                "converted_count": converted,
                "lost_count":      lost,
                "active_count":    max(count - converted - lost, 0),
                "conversion_rate": (converted / count * 100) if count else 0.0,
                "total_budget":    budget,
                "avg_budget":      budget / count if count else 0.0,
            })

        # "Other" — leads that match none of the defined source patterns
        all_known = or_(*[fn() for _, _, fn in SOURCE_CATALOGUE])
        other_base   = self._leads(date_from, date_to, user_id).filter(~all_known)
        other_joined = self._leads_with_stage(date_from, date_to, user_id).filter(~all_known)
        other_count  = other_base.count()
        if other_count:
            other_conv = other_joined.filter(_closed_expr()).count()
            other_lost = other_joined.filter(_lost_expr()).count()
            other_bgt  = float(other_base.with_entities(
                func.coalesce(func.sum(Lead.budget), 0.0)
            ).scalar() or 0)
            rows.append({
                "source_key":      "other",
                "source_label":    "Outros",
                "lead_count":      other_count,
                "converted_count": other_conv,
                "lost_count":      other_lost,
                "active_count":    max(other_count - other_conv - other_lost, 0),
                "conversion_rate": (other_conv / other_count * 100) if other_count else 0.0,
                "total_budget":    other_bgt,
                "avg_budget":      other_bgt / other_count if other_count else 0.0,
            })

        # Filter zero-count sources (keep only sources with data)
        rows = [r for r in rows if r["lead_count"] > 0]
        rows.sort(key=lambda x: x["lead_count"], reverse=True)
        return rows, total
