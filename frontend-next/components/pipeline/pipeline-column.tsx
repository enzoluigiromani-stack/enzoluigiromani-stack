"use client";

import { useDroppable } from "@dnd-kit/core";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowDown, Plus } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { PipelineCard } from "./pipeline-card";
import { cn } from "@/lib/utils";
import type { KanbanColumn } from "@/types";

interface PipelineColumnProps {
  column: KanbanColumn;
  isAnyDragging: boolean;
}

export function PipelineColumn({ column, isAnyDragging }: PipelineColumnProps) {
  const { stage, leads } = column;
  const { setNodeRef, isOver } = useDroppable({ id: `col-${stage.id}` });

  const totalValue = leads.reduce((sum, l) => sum + (l.value ?? 0), 0);
  const formattedValue =
    totalValue > 0
      ? totalValue.toLocaleString("pt-BR", {
          style: "currency",
          currency: "BRL",
          notation: "compact",
          maximumFractionDigits: 1,
        } as Intl.NumberFormatOptions)
      : null;

  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2 }}
      className="flex flex-col w-[272px] shrink-0"
    >
      {/* Cabeçalho da coluna */}
      <div className="flex items-center justify-between mb-3 px-1">
        <div className="flex items-center gap-2 min-w-0">
          <div
            className="h-2.5 w-2.5 rounded-full shrink-0"
            style={{ backgroundColor: stage.color ?? "#6366f1" }}
          />
          <span className="text-sm font-semibold truncate">{stage.name}</span>
          <Badge
            variant="secondary"
            className="text-[10px] px-1.5 py-0 h-4 shrink-0 font-medium"
          >
            {leads.length}
          </Badge>
        </div>
        {formattedValue && (
          <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold shrink-0 ml-1">
            {formattedValue}
          </span>
        )}
      </div>

      {/* Zona de drop */}
      <div
        ref={setNodeRef}
        className={cn(
          "flex flex-col gap-2 rounded-xl p-2 min-h-[420px] flex-1 transition-all duration-200",
          isOver
            ? "bg-primary/8 ring-2 ring-primary/30 ring-dashed"
            : isAnyDragging
            ? "bg-muted/25 ring-1 ring-border/60 ring-dashed"
            : "bg-muted/40"
        )}
      >
        <AnimatePresence mode="popLayout">
          {leads.map((lead) => (
            <PipelineCard key={lead.id} lead={lead} stageColor={stage.color} />
          ))}
        </AnimatePresence>

        {/* Empty state */}
        {leads.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className={cn(
              "flex flex-col items-center justify-center flex-1 gap-2 rounded-lg",
              "min-h-[160px]"
            )}
          >
            {isOver ? (
              <>
                <motion.div
                  animate={{ y: [0, 4, 0] }}
                  transition={{ repeat: Infinity, duration: 0.8 }}
                >
                  <ArrowDown className="h-5 w-5 text-primary" />
                </motion.div>
                <p className="text-xs font-medium text-primary">Soltar aqui</p>
              </>
            ) : (
              <>
                <Plus className="h-4 w-4 text-muted-foreground/40" />
                <p className="text-xs text-muted-foreground/50">
                  {isAnyDragging ? "Soltar aqui" : "Sem leads"}
                </p>
              </>
            )}
          </motion.div>
        )}

        {/* Drop hint at bottom when column has cards */}
        {leads.length > 0 && isOver && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 36 }}
            className="flex items-center justify-center rounded-lg border-2 border-dashed border-primary/30 text-xs text-primary/60"
          >
            Soltar aqui
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
