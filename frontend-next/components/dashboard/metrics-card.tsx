"use client";

import { useEffect, useRef, useState } from "react";
import { type LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface MetricsCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon: LucideIcon;
  trend?: { value: number; label: string };
  variant?: "default" | "warning" | "danger" | "success";
}

const variantStyles = {
  default: "text-primary bg-primary/10",
  warning: "text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20 dark:text-yellow-400",
  danger:  "text-destructive bg-destructive/10",
  success: "text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 dark:text-emerald-400",
};

export function MetricsCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
  variant = "default",
}: MetricsCardProps) {
  const prevRef = useRef(value);
  const [flash, setFlash] = useState(false);

  useEffect(() => {
    if (prevRef.current !== value) {
      prevRef.current = value;
      setFlash(true);
      const t = setTimeout(() => setFlash(false), 600);
      return () => clearTimeout(t);
    }
  }, [value]);

  return (
    <Card
      className={cn(
        "hover:shadow-md transition-all animate-fade-in",
        flash && "ring-2 ring-primary/30 shadow-md",
      )}
    >
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-1 flex-1">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p
              className={cn(
                "text-3xl font-bold transition-all duration-300",
                flash && "text-primary scale-105",
              )}
            >
              {value}
            </p>
            {description && (
              <p className="text-xs text-muted-foreground">{description}</p>
            )}
            {trend && (
              <p
                className={cn(
                  "text-xs font-medium",
                  trend.value >= 0 ? "text-emerald-600" : "text-destructive",
                )}
              >
                {trend.value >= 0 ? "+" : ""}{trend.value}% {trend.label}
              </p>
            )}
          </div>
          <div className={cn("p-3 rounded-lg shrink-0", variantStyles[variant])}>
            <Icon className="h-5 w-5" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
