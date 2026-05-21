"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { TimelineResponse } from "@/types/analytics";
import { useTheme } from "@/hooks/use-theme";

interface TimelineChartProps {
  data?: TimelineResponse;
  loading?: boolean;
}

function formatLabel(period: string, granularity: string): string {
  if (granularity === "day") {
    const [, m, d] = period.split("-");
    return `${d}/${m}`;
  }
  if (granularity === "week") {
    const parts = period.includes("-W") ? period.split("-W") : period.split("-");
    return `S${parts[1]}/${parts[0]?.slice(2)}`;
  }
  const [y, m] = period.split("-");
  const months = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"];
  return `${months[Number(m) - 1]} ${y?.slice(2)}`;
}

export function TimelineChart({ data, loading }: TimelineChartProps) {
  const { chartColors } = useTheme();

  if (loading) {
    return (
      <Card>
        <CardHeader><CardTitle className="text-base">Evolução de Leads</CardTitle></CardHeader>
        <CardContent>
          <div className="h-64 bg-muted animate-pulse rounded" />
        </CardContent>
      </Card>
    );
  }

  const chartData = (data?.points ?? []).map((p) => ({
    period: formatLabel(p.period, data?.granularity ?? "month"),
    "Novos leads": p.new_leads,
    "Convertidos": p.converted_leads,
    "Receita (R$)": p.closed_revenue,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Evolução de Leads</CardTitle>
        <p className="text-xs text-muted-foreground">{data?.period_label}</p>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={260}>
          <AreaChart data={chartData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorNew" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorConv" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
            <XAxis dataKey="period" tick={{ fontSize: 11, fill: chartColors.tick }} tickLine={false} axisLine={false} />
            <YAxis tick={{ fontSize: 11, fill: chartColors.tick }} tickLine={false} axisLine={false} width={36} />
            <Tooltip
              contentStyle={{
                borderRadius: 8,
                border: `1px solid ${chartColors.border}`,
                backgroundColor: chartColors.tooltip,
                color: chartColors.text,
                fontSize: 12,
              }}
            />
            <Legend wrapperStyle={{ fontSize: 12, color: chartColors.tick }} />
            <Area type="monotone" dataKey="Novos leads" stroke="#6366f1" fill="url(#colorNew)" strokeWidth={2} dot={false} />
            <Area type="monotone" dataKey="Convertidos"  stroke="#10b981" fill="url(#colorConv)" strokeWidth={2} dot={false} />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
