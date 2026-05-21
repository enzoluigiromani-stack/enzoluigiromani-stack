"use client";

import { useEffect, useRef, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: number;
  format?: "number" | "currency" | "percent";
  trend?: number; // positive = up, negative = down
  icon?: React.ReactNode;
  className?: string;
  loading?: boolean;
  suffix?: string;
}

function useCountUp(target: number, duration = 800) {
  const [current, setCurrent] = useState(0);
  const frameRef = useRef<number>(0);
  const startRef = useRef<number>(0);
  const startValRef = useRef<number>(0);

  useEffect(() => {
    startRef.current = performance.now();
    startValRef.current = current;
    const delta = target - startValRef.current;

    const step = (now: number) => {
      const elapsed = now - startRef.current;
      const progress = Math.min(elapsed / duration, 1);
      // easeOutCubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setCurrent(Math.round(startValRef.current + delta * eased));
      if (progress < 1) frameRef.current = requestAnimationFrame(step);
    };

    frameRef.current = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frameRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target]);

  return current;
}

function formatValue(value: number, format: MetricCardProps["format"], suffix?: string): string {
  if (format === "currency") {
    return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 }).format(value);
  }
  if (format === "percent") {
    return `${value.toFixed(1)}%`;
  }
  return new Intl.NumberFormat("pt-BR").format(value) + (suffix ? ` ${suffix}` : "");
}

export function MetricCard({ title, value, format = "number", trend, icon, className, loading, suffix }: MetricCardProps) {
  const animated = useCountUp(loading ? 0 : value);

  if (loading) {
    return (
      <Card className={cn("overflow-hidden", className)}>
        <CardContent className="p-5">
          <div className="h-4 w-24 bg-muted animate-pulse rounded mb-3" />
          <div className="h-8 w-32 bg-muted animate-pulse rounded mb-2" />
          <div className="h-3 w-16 bg-muted animate-pulse rounded" />
        </CardContent>
      </Card>
    );
  }

  const TrendIcon = trend === undefined || trend === 0 ? Minus : trend > 0 ? TrendingUp : TrendingDown;
  const trendColor = trend === undefined || trend === 0
    ? "text-muted-foreground"
    : trend > 0 ? "text-emerald-500" : "text-red-500";

  return (
    <Card className={cn("overflow-hidden transition-shadow hover:shadow-md", className)}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <p className="text-sm font-medium text-muted-foreground leading-none mb-2">{title}</p>
          {icon && <span className="text-muted-foreground">{icon}</span>}
        </div>
        <p className="text-2xl font-bold tracking-tight text-foreground">
          {format === "currency"
            ? formatValue(value, format, suffix)
            : format === "percent"
              ? formatValue(value, format, suffix)
              : formatValue(animated, format, suffix)}
        </p>
        {trend !== undefined && (
          <div className={cn("flex items-center gap-1 mt-1.5 text-xs font-medium", trendColor)}>
            <TrendIcon className="h-3 w-3" />
            <span>{Math.abs(trend).toFixed(1)}% vs período anterior</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
