// Analytics types — mirror backend schemas/analytics.py

export interface AnalyticsFilters {
  date_from?: string; // YYYY-MM-DD
  date_to?: string;
  user_id?: number;
  source?: string;
  granularity?: "day" | "week" | "month";
}

// Overview
export interface OverviewMetrics {
  period_label: string;
  total_leads: number;
  new_leads: number;
  active_leads: number;
  converted_leads: number;
  lost_leads: number;
  conversion_rate: number;
  lost_rate: number;
  closed_revenue: number;
  estimated_revenue: number;
  total_pipeline_value: number;
  avg_deal_size: number;
  tasks_completed: number;
  tasks_pending: number;
  tasks_overdue: number;
  open_conversations: number;
}

// Leads by stage
export interface StageMetrics {
  stage_id: number;
  stage_name: string;
  stage_color: string | null;
  stage_order: number;
  lead_count: number;
  total_budget: number;
  avg_budget: number;
  pct_of_total: number;
  conversion_from_prev: number | null;
}

export interface LeadsByStageResponse {
  stages: StageMetrics[];
  no_stage_count: number;
  total_leads: number;
  period_label: string;
}

// Funnel
export interface FunnelStep {
  stage_id: number;
  stage_name: string;
  stage_color: string | null;
  stage_order: number;
  lead_count: number;
  entered_pct: number;
  converted_from_prev: number | null;
}

export interface ConversionFunnelResponse {
  steps: FunnelStep[];
  overall_conversion_rate: number;
}

// Revenue
export interface MonthlyBreakdown {
  period: string;
  new_leads: number;
  closed_leads: number;
  closed_revenue: number;
  avg_deal_size: number;
}

export interface RevenueResponse {
  closed_revenue: number;
  estimated_revenue: number;
  total_pipeline_value: number;
  avg_deal_value: number;
  total_deals_closed: number;
  total_deals_open: number;
  monthly: MonthlyBreakdown[];
  period_label: string;
}

// By user
export interface UserPerformance {
  user_id: number;
  user_name: string;
  user_email: string;
  leads_assigned: number;
  leads_converted: number;
  leads_lost: number;
  leads_active: number;
  conversion_rate: number;
  closed_revenue: number;
  estimated_revenue: number;
  avg_deal_size: number;
  tasks_completed: number;
  tasks_pending: number;
  tasks_overdue: number;
}

export interface ByUserResponse {
  users: UserPerformance[];
  period_label: string;
}

// By source
export interface SourceBreakdown {
  source_key: string;
  source_label: string;
  lead_count: number;
  converted_count: number;
  lost_count: number;
  active_count: number;
  conversion_rate: number;
  total_budget: number;
  avg_budget: number;
  pct_of_total: number;
}

export interface BySourceResponse {
  sources: SourceBreakdown[];
  total_leads: number;
  period_label: string;
}

// Timeline
export interface TimelinePoint {
  period: string;
  new_leads: number;
  converted_leads: number;
  closed_revenue: number;
}

export interface TimelineResponse {
  points: TimelinePoint[];
  granularity: "day" | "week" | "month";
  total_new: number;
  total_converted: number;
  total_revenue: number;
  period_label: string;
}
