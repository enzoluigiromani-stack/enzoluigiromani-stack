"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { LeadsByStageResponse } from "@/types/analytics";

interface StageChartProps {
  data?: LeadsByStageResponse;
  loading?: boolean;
}

const DEFAULT_COLOR = "#6366f1";

export function StageChart({ data, loading }: StageChartProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader><CardTitle className="text-base">Leads por Etapa</CardTitle></CardHeader>
        <CardContent>
          <div className="h-64 bg-muted animate-pulse rounded" />
        </CardContent>
      </Card>
    );
  }

  const chartData = (data?.stages ?? []).map((s) => ({
    name: s.stage_name,
    leads: s.lead_count,
    receita: s.total_budget,
    color: s.stage_color ?? DEFAULT_COLOR,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Leads por Etapa do Pipeline</CardTitle>
        <p className="text-xs text-muted-foreground">{data?.period_label}</p>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={chartData} layout="vertical" margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="hsl(var(--border))" />
            <XAxis type="number" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              width={90}
            />
            <Tooltip
              formatter={(val) => [`${val} leads`, "Leads"]}
              contentStyle={{ borderRadius: 8, border: "1px solid hsl(var(--border))", fontSize: 12 }}
            />
            <Bar dataKey="leads" radius={[0, 4, 4, 0]}>
              {chartData.map((entry, i) => (
                <Cell key={i} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
