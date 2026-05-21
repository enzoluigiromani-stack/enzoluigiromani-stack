"""
Schemas de Analytics — todos os shapes de request/response.
Preparados para real-time, exportação e dashboards avançados futuros.
"""
from __future__ import annotations

from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field


# ── Filter params (shared across endpoints) ───────────────────────────────────

class AnalyticsFilters(BaseModel):
    date_from: Optional[date] = None
    date_to:   Optional[date] = None
    user_id:   Optional[int]  = None
    source:    Optional[str]  = None   # meta_ads|instagram|whatsapp|google|referral|organic


# ── Overview ──────────────────────────────────────────────────────────────────

class OverviewMetrics(BaseModel):
    period_label:        str
    total_leads:         int
    new_leads:           int    # created in period
    active_leads:        int    # in pipeline (not closed/lost)
    converted_leads:     int    # in "fechado" stage
    lost_leads:          int    # in "perdido" stage
    conversion_rate:     float  # converted / total × 100
    lost_rate:           float  # lost / total × 100
    closed_revenue:      float  # Σ budget of closed leads
    estimated_revenue:   float  # Σ budget of active leads
    total_pipeline_value: float # closed + estimated
    avg_deal_size:       float  # closed_revenue / converted, or 0
    tasks_completed:     int
    tasks_pending:       int
    tasks_overdue:       int
    open_conversations:  int


# ── Leads by Stage ────────────────────────────────────────────────────────────

class StageMetrics(BaseModel):
    stage_id:    Optional[int]
    stage_name:  str
    stage_color: Optional[str]
    stage_order: int
    lead_count:  int
    total_budget: float
    avg_budget:   float
    pct_of_total: float          # % of all leads
    conversion_from_prev: Optional[float]  # funnel drop from previous stage (%)


class LeadsByStageResponse(BaseModel):
    stages:        List[StageMetrics]
    no_stage_count: int
    total_leads:   int
    period_label:  str


# ── Conversion Funnel ─────────────────────────────────────────────────────────

class FunnelStep(BaseModel):
    stage_id:    Optional[int]
    stage_name:  str
    stage_color: Optional[str]
    stage_order: int
    lead_count:  int
    entered_pct:          float          # % relative to first stage
    converted_from_prev:  Optional[float] # % that progressed from previous step


class ConversionFunnelResponse(BaseModel):
    steps:                    List[FunnelStep]
    overall_conversion_rate:  float   # first stage → closed stage


# ── Revenue ───────────────────────────────────────────────────────────────────

class MonthlyBreakdown(BaseModel):
    period:         str    # "2025-01"
    new_leads:      int
    closed_leads:   int
    closed_revenue: float
    avg_deal_size:  float


class RevenueResponse(BaseModel):
    closed_revenue:      float
    estimated_revenue:   float
    total_pipeline_value: float
    avg_deal_value:      float
    total_deals_closed:  int
    total_deals_open:    int
    monthly:             List[MonthlyBreakdown]
    period_label:        str


# ── By User ───────────────────────────────────────────────────────────────────

class UserPerformance(BaseModel):
    user_id:           int
    user_name:         str
    user_email:        str
    leads_assigned:    int
    leads_converted:   int
    leads_lost:        int
    leads_active:      int
    conversion_rate:   float
    closed_revenue:    float
    estimated_revenue: float
    avg_deal_size:     float
    tasks_completed:   int
    tasks_pending:     int
    tasks_overdue:     int


class ByUserResponse(BaseModel):
    users:        List[UserPerformance]
    period_label: str


# ── By Source ─────────────────────────────────────────────────────────────────

class SourceBreakdown(BaseModel):
    source_key:      str    # "meta_ads", "instagram", ...
    source_label:    str    # "Meta Ads", "Instagram", ...
    lead_count:      int
    converted_count: int
    lost_count:      int
    active_count:    int
    conversion_rate: float
    total_budget:    float
    avg_budget:      float
    pct_of_total:    float


class BySourceResponse(BaseModel):
    sources:      List[SourceBreakdown]
    total_leads:  int
    period_label: str


# ── Timeline ──────────────────────────────────────────────────────────────────

class TimelinePoint(BaseModel):
    period:          str    # "2025-01-15" | "2025-01" | "2025-W03"
    new_leads:       int
    converted_leads: int
    closed_revenue:  float


class TimelineResponse(BaseModel):
    points:          List[TimelinePoint]
    granularity:     str    # "day" | "week" | "month"
    total_new:       int
    total_converted: int
    total_revenue:   float
    period_label:    str
