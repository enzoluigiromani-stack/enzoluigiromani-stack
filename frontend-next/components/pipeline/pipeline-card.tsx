"use client";

import { useDraggable } from "@dnd-kit/core";
import { motion } from "framer-motion";
import {
  Mail,
  Phone,
  DollarSign,
  GripVertical,
  Building2,
  Globe,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { Lead } from "@/types";
import { useRouter } from "next/navigation";

const SOURCE_COLORS: Record<string, string> = {
  facebook:  "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
  google:    "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300",
  organic:   "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300",
  instagram: "bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-300",
  whatsapp:  "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300",
  email:     "bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-300",
  linkedin:  "bg-sky-100 text-sky-700 dark:bg-sky-900/30 dark:text-sky-300",
};

export interface PipelineCardDisplayProps {
  lead: Lead;
  stageColor?: string;
  isOverlay?: boolean;
}

// Componente de display puro — usado tanto no card normal quanto no DragOverlay
export function PipelineCardDisplay({ lead, stageColor, isOverlay = false }: PipelineCardDisplayProps) {
  const sourceKey = lead.utm_source?.toLowerCase();
  const sourceColor = sourceKey ? (SOURCE_COLORS[sourceKey] ?? "bg-secondary text-secondary-foreground") : null;

  const formatValue = (v: number) =>
    v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

  return (
    <div
      className={cn(
        "relative bg-card border border-border rounded-xl overflow-hidden",
        "transition-all duration-150",
        isOverlay
          ? "shadow-2xl ring-2 ring-primary/25 scale-[1.03] rotate-[0.8deg]"
          : "shadow-sm"
      )}
    >
      {/* Accent lateral do estágio */}
      {stageColor && (
        <div
          className="absolute left-0 top-0 bottom-0 w-[3px]"
          style={{ backgroundColor: stageColor }}
        />
      )}

      <div className="p-3 pl-[14px]">
        {/* Nome + handle */}
        <div className="flex items-start gap-2 mb-2">
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold leading-snug text-foreground line-clamp-1">
              {lead.name}
            </p>
            {lead.company && (
              <p className="text-xs text-muted-foreground mt-0.5 flex items-center gap-1 line-clamp-1">
                <Building2 className="h-2.5 w-2.5 shrink-0" />
                {lead.company}
              </p>
            )}
          </div>
          {!isOverlay && (
            <GripVertical className="h-4 w-4 shrink-0 mt-0.5 text-muted-foreground/30 group-hover:text-muted-foreground/60 transition-colors" />
          )}
        </div>

        {/* Contato */}
        {(lead.email || lead.phone) && (
          <div className="space-y-0.5 mb-2.5">
            {lead.email && (
              <p className="text-[11px] text-muted-foreground flex items-center gap-1.5 truncate">
                <Mail className="h-2.5 w-2.5 shrink-0" />
                {lead.email}
              </p>
            )}
            {lead.phone && (
              <p className="text-[11px] text-muted-foreground flex items-center gap-1.5">
                <Phone className="h-2.5 w-2.5 shrink-0" />
                {lead.phone}
              </p>
            )}
          </div>
        )}

        {/* Valor */}
        {lead.value != null && lead.value > 0 && (
          <p className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1 mb-2.5">
            <DollarSign className="h-3 w-3" />
            {formatValue(lead.value)}
          </p>
        )}

        {/* Tags + Origem */}
        {((lead.tags && lead.tags.length > 0) || sourceColor) && (
          <div className="flex flex-wrap gap-1">
            {sourceColor && lead.utm_source && (
              <span className={cn("px-1.5 py-0.5 rounded-full text-[10px] font-medium flex items-center gap-0.5", sourceColor)}>
                <Globe className="h-2 w-2" />
                {lead.utm_source}
              </span>
            )}
            {lead.tags?.slice(0, 2).map((tag) => (
              <span
                key={tag}
                className="px-1.5 py-0.5 rounded-full text-[10px] font-medium bg-secondary text-secondary-foreground"
              >
                {tag}
              </span>
            ))}
            {(lead.tags?.length ?? 0) > 2 && (
              <span className="text-[10px] text-muted-foreground/60 self-center">
                +{(lead.tags?.length ?? 0) - 2}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export interface PipelineCardProps {
  lead: Lead;
  stageColor?: string;
}

export function PipelineCard({ lead, stageColor }: PipelineCardProps) {
  const router = useRouter();
  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({
    id: `card-${lead.id}`,
    data: { lead, stageColor },
  });

  return (
    <motion.div
      ref={setNodeRef}
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: isDragging ? 0.35 : 1, y: 0 }}
      exit={{ opacity: 0, y: -4, scale: 0.97 }}
      transition={{ duration: 0.14, ease: "easeOut" }}
      layout
      className={cn("group cursor-pointer", isDragging && "pointer-events-none")}
      onClick={() => router.push(`/leads/${lead.id}`)}
      {...attributes}
      {...listeners}
    >
      <PipelineCardDisplay lead={lead} stageColor={stageColor} />
    </motion.div>
  );
}
