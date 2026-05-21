"use client";

import { motion } from "framer-motion";
import { Users, TrendingUp, Trophy, Layers } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: React.ElementType;
  iconBg: string;
  iconColor: string;
  index: number;
}

function StatCard({ label, value, icon: Icon, iconBg, iconColor, index }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: index * 0.05 }}
      className="flex items-center gap-3 px-4 py-3 bg-card border border-border rounded-xl"
    >
      <div className={cn("p-2 rounded-lg shrink-0", iconBg)}>
        <Icon className={cn("h-4 w-4", iconColor)} />
      </div>
      <div className="min-w-0">
        <p className="text-[11px] text-muted-foreground leading-none mb-1">{label}</p>
        <p className="text-sm font-bold leading-none text-foreground truncate">{value}</p>
      </div>
    </motion.div>
  );
}

interface PipelineHeaderProps {
  totalLeads: number;
  totalValue: number;
  stageCount: number;
  wonLeads: number;
}

export function PipelineHeader({ totalLeads, totalValue, stageCount, wonLeads }: PipelineHeaderProps) {
  const formattedValue = totalValue.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
    notation: "compact",
    maximumFractionDigits: 1,
  } as Intl.NumberFormatOptions);

  const stats = [
    {
      label: "Leads no pipeline",
      value: totalLeads,
      icon: Users,
      iconBg: "bg-blue-50 dark:bg-blue-900/20",
      iconColor: "text-blue-600 dark:text-blue-400",
    },
    {
      label: "Valor total",
      value: formattedValue,
      icon: TrendingUp,
      iconBg: "bg-emerald-50 dark:bg-emerald-900/20",
      iconColor: "text-emerald-600 dark:text-emerald-400",
    },
    {
      label: "Estágios ativos",
      value: stageCount,
      icon: Layers,
      iconBg: "bg-violet-50 dark:bg-violet-900/20",
      iconColor: "text-violet-600 dark:text-violet-400",
    },
    {
      label: "Ganhos",
      value: wonLeads,
      icon: Trophy,
      iconBg: "bg-amber-50 dark:bg-amber-900/20",
      iconColor: "text-amber-600 dark:text-amber-400",
    },
  ] as const;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {stats.map((stat, i) => (
        <StatCard key={stat.label} {...stat} index={i} />
      ))}
    </div>
  );
}
