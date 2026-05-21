import { useQuery } from "@tanstack/react-query";
import { analyticsService } from "@/services/analytics.service";
import type { AnalyticsFilters } from "@/types/analytics";

const STALE = 2 * 60 * 1000; // 2 min

export function useOverview(filters: AnalyticsFilters = {}) {
  return useQuery({
    queryKey: ["analytics", "overview", filters],
    queryFn: () => analyticsService.getOverview(filters),
    staleTime: STALE,
  });
}

export function useLeadsByStage(filters: AnalyticsFilters = {}) {
  return useQuery({
    queryKey: ["analytics", "leads-by-stage", filters],
    queryFn: () => analyticsService.getLeadsByStage(filters),
    staleTime: STALE,
  });
}

export function useFunnel(filters: AnalyticsFilters = {}) {
  return useQuery({
    queryKey: ["analytics", "funnel", filters],
    queryFn: () => analyticsService.getFunnel(filters),
    staleTime: STALE,
  });
}

export function useRevenue(filters: AnalyticsFilters = {}) {
  return useQuery({
    queryKey: ["analytics", "revenue", filters],
    queryFn: () => analyticsService.getRevenue(filters),
    staleTime: STALE,
  });
}

export function useByUser(filters: Pick<AnalyticsFilters, "date_from" | "date_to"> = {}) {
  return useQuery({
    queryKey: ["analytics", "by-user", filters],
    queryFn: () => analyticsService.getByUser(filters),
    staleTime: STALE,
  });
}

export function useBySource(filters: AnalyticsFilters = {}) {
  return useQuery({
    queryKey: ["analytics", "by-source", filters],
    queryFn: () => analyticsService.getBySource(filters),
    staleTime: STALE,
  });
}

export function useTimeline(filters: AnalyticsFilters = {}) {
  return useQuery({
    queryKey: ["analytics", "timeline", filters],
    queryFn: () => analyticsService.getTimeline(filters),
    staleTime: STALE,
  });
}
