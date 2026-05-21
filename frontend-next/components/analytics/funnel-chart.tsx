"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { ConversionFunnelResponse } from "@/types/analytics";

interface FunnelChartProps {
  data?: ConversionFunnelResponse;
  loading?: boolean;
}

const DEFAULT_COLOR = "#6366f1";

export function FunnelChart({ data, loading }: FunnelChartProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader><CardTitle className="text-base">Funil de Conversão</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-12 bg-muted animate-pulse rounded" />
          ))}
        </CardContent>
      </Card>
    );
  }

  const steps = data?.steps ?? [];
  const maxCount = steps[0]?.lead_count ?? 1;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <CardTitle className="text-base">Funil de Conversão</CardTitle>
          {data && (
            <Badge variant="secondary" className="text-xs">
              {data.overall_conversion_rate.toFixed(1)}% geral
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        {steps.map((step, i) => {
          const widthPct = Math.max((step.lead_count / maxCount) * 100, 8);
          const color = step.stage_color ?? DEFAULT_COLOR;
          return (
            <div key={step.stage_id} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="font-medium text-foreground truncate max-w-[160px]">{step.stage_name}</span>
                <span className="text-muted-foreground tabular-nums">{step.lead_count} leads</span>
              </div>
              <div className="h-8 bg-muted rounded-md overflow-hidden">
                <div
                  className="h-full rounded-md transition-all duration-700 flex items-center px-2"
                  style={{ width: `${widthPct}%`, backgroundColor: color }}
                >
                  <span className="text-white text-xs font-semibold">
                    {step.entered_pct.toFixed(0)}%
                  </span>
                </div>
              </div>
              {i > 0 && step.converted_from_prev !== null && (
                <p className={cn("text-xs", step.converted_from_prev >= 50 ? "text-emerald-600" : "text-amber-600")}>
                  ↓ {step.converted_from_prev.toFixed(1)}% avançaram da etapa anterior
                </p>
              )}
            </div>
          );
        })}
        {steps.length === 0 && (
          <p className="text-sm text-muted-foreground text-center py-8">Sem dados no período</p>
        )}
      </CardContent>
    </Card>
  );
}
