"use client";

import { useState, useCallback } from "react";
import {
  BarChart2,
  TrendingUp,
  Users,
  DollarSign,
  Target,
  MessageSquare,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  WifiOff,
} from "lucide-react";
import { Separator } from "@/components/ui/separator";
import { useRealtimeStatus } from "@/hooks/use-realtime";
import { cn } from "@/lib/utils";
import { MetricCard } from "@/components/analytics/metric-card";
import { AnalyticsFiltersBar } from "@/components/analytics/analytics-filters";
import { TimelineChart } from "@/components/analytics/timeline-chart";
import { SourceChart } from "@/components/analytics/source-chart";
import { StageChart } from "@/components/analytics/stage-chart";
import { FunnelChart } from "@/components/analytics/funnel-chart";
import { UserTable } from "@/components/analytics/user-table";
import {
  useOverview,
  useTimeline,
  useBySource,
  useLeadsByStage,
  useFunnel,
  useByUser,
} from "@/hooks/use-analytics";
import type { AnalyticsFilters } from "@/types/analytics";

function LiveDot() {
  const status = useRealtimeStatus();
  return (
    <span
      title={status === "connected" ? "Ao vivo" : status === "connecting" ? "Conectando…" : "Offline"}
      className={cn(
        "flex items-center justify-center h-5 w-5 rounded-full transition-colors",
        status === "connected" ? "text-emerald-500" : "text-muted-foreground/40",
      )}
    >
      {status === "connected" ? (
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-60" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
        </span>
      ) : status === "connecting" ? (
        <RefreshCw className="h-3.5 w-3.5 animate-spin" />
      ) : (
        <WifiOff className="h-3.5 w-3.5" />
      )}
    </span>
  );
}

function defaultFilters(): AnalyticsFilters {
  const to = new Date();
  const from = new Date();
  from.setDate(from.getDate() - 30);
  return {
    date_from: from.toISOString().slice(0, 10),
    date_to: to.toISOString().slice(0, 10),
  };
}

export default function ReportsPage() {
  const [filters, setFilters] = useState<AnalyticsFilters>(defaultFilters);

  const handleFilters = useCallback((f: AnalyticsFilters) => setFilters(f), []);

  const overview  = useOverview(filters);
  const timeline  = useTimeline(filters);
  const bySource  = useBySource(filters);
  const byStage   = useLeadsByStage(filters);
  const funnel    = useFunnel(filters);
  const byUser    = useByUser({ date_from: filters.date_from, date_to: filters.date_to });

  const ov = overview.data;

  return (
    <div className="flex flex-col gap-6 p-6 max-w-[1400px] mx-auto">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <BarChart2 className="h-6 w-6 text-primary" />
          <div>
            <h1 className="text-xl font-bold">Relatórios & Analytics</h1>
            <p className="text-xs text-muted-foreground">
              {ov?.period_label ?? "Carregando…"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {overview.dataUpdatedAt > 0 && (
            <span className="text-xs text-muted-foreground">
              Atualizado às{" "}
              {new Date(overview.dataUpdatedAt).toLocaleTimeString("pt-BR", {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
              })}
            </span>
          )}
          <LiveDot />
        </div>
      </div>

      {/* Filters */}
      <AnalyticsFiltersBar filters={filters} onChange={handleFilters} />

      <Separator />

      {/* KPI grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3">
        <MetricCard
          title="Total de leads"
          value={ov?.total_leads ?? 0}
          icon={<Users className="h-4 w-4" />}
          loading={overview.isLoading}
        />
        <MetricCard
          title="Leads ativos"
          value={ov?.active_leads ?? 0}
          icon={<Target className="h-4 w-4" />}
          loading={overview.isLoading}
        />
        <MetricCard
          title="Convertidos"
          value={ov?.converted_leads ?? 0}
          format="number"
          icon={<TrendingUp className="h-4 w-4" />}
          loading={overview.isLoading}
        />
        <MetricCard
          title="Taxa de conversão"
          value={ov?.conversion_rate ?? 0}
          format="percent"
          icon={<TrendingUp className="h-4 w-4" />}
          loading={overview.isLoading}
        />
        <MetricCard
          title="Receita fechada"
          value={ov?.closed_revenue ?? 0}
          format="currency"
          icon={<DollarSign className="h-4 w-4" />}
          loading={overview.isLoading}
        />
        <MetricCard
          title="Rec. estimada"
          value={ov?.estimated_revenue ?? 0}
          format="currency"
          icon={<DollarSign className="h-4 w-4" />}
          loading={overview.isLoading}
        />
      </div>

      {/* Secondary KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <MetricCard
          title="Ticket médio"
          value={ov?.avg_deal_size ?? 0}
          format="currency"
          loading={overview.isLoading}
        />
        <MetricCard
          title="Conversas abertas"
          value={ov?.open_conversations ?? 0}
          icon={<MessageSquare className="h-4 w-4" />}
          loading={overview.isLoading}
        />
        <MetricCard
          title="Tarefas concluídas"
          value={ov?.tasks_completed ?? 0}
          icon={<CheckCircle2 className="h-4 w-4" />}
          loading={overview.isLoading}
        />
        <MetricCard
          title="Tarefas atrasadas"
          value={ov?.tasks_overdue ?? 0}
          icon={<AlertTriangle className="h-4 w-4" />}
          loading={overview.isLoading}
        />
      </div>

      <Separator />

      {/* Charts row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <TimelineChart data={timeline.data} loading={timeline.isLoading} />
        </div>
        <SourceChart data={bySource.data} loading={bySource.isLoading} />
      </div>

      {/* Charts row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <StageChart data={byStage.data} loading={byStage.isLoading} />
        <FunnelChart data={funnel.data} loading={funnel.isLoading} />
      </div>

      {/* User table */}
      <UserTable data={byUser.data} loading={byUser.isLoading} />
    </div>
  );
}
