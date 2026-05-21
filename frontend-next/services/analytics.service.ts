import { api } from "./api";
import type {
  AnalyticsFilters,
  BySourceResponse,
  ByUserResponse,
  ConversionFunnelResponse,
  LeadsByStageResponse,
  OverviewMetrics,
  RevenueResponse,
  TimelineResponse,
} from "@/types/analytics";

function buildParams(filters: AnalyticsFilters): Record<string, string> {
  const p: Record<string, string> = {};
  if (filters.date_from) p.date_from = filters.date_from;
  if (filters.date_to)   p.date_to   = filters.date_to;
  if (filters.user_id)   p.user_id   = String(filters.user_id);
  if (filters.source)    p.source    = filters.source;
  if (filters.granularity) p.granularity = filters.granularity;
  return p;
}

export const analyticsService = {
  getOverview: async (filters: AnalyticsFilters = {}): Promise<OverviewMetrics> => {
    const { data } = await api.get("/analytics/overview", { params: buildParams(filters) });
    return data;
  },

  getLeadsByStage: async (filters: AnalyticsFilters = {}): Promise<LeadsByStageResponse> => {
    const { data } = await api.get("/analytics/leads-by-stage", { params: buildParams(filters) });
    return data;
  },

  getFunnel: async (filters: AnalyticsFilters = {}): Promise<ConversionFunnelResponse> => {
    const { data } = await api.get("/analytics/funnel", { params: buildParams(filters) });
    return data;
  },

  getRevenue: async (filters: AnalyticsFilters = {}): Promise<RevenueResponse> => {
    const { data } = await api.get("/analytics/revenue", { params: buildParams(filters) });
    return data;
  },

  getByUser: async (filters: Pick<AnalyticsFilters, "date_from" | "date_to"> = {}): Promise<ByUserResponse> => {
    const { data } = await api.get("/analytics/by-user", { params: buildParams(filters) });
    return data;
  },

  getBySource: async (filters: AnalyticsFilters = {}): Promise<BySourceResponse> => {
    const { data } = await api.get("/analytics/by-source", { params: buildParams(filters) });
    return data;
  },

  getTimeline: async (filters: AnalyticsFilters = {}): Promise<TimelineResponse> => {
    const { data } = await api.get("/analytics/timeline", { params: buildParams(filters) });
    return data;
  },
};
