"use client";

import { useState, useCallback } from "react";
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  TouchSensor,
  useSensor,
  useSensors,
  type DragStartEvent,
  type DragEndEvent,
} from "@dnd-kit/core";
import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, RefreshCw, Inbox, Wifi, WifiOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PipelineColumn } from "./pipeline-column";
import { PipelineHeader } from "./pipeline-header";
import { PipelineSkeleton } from "./pipeline-skeleton";
import { PipelineCardDisplay } from "./pipeline-card";
import { usePipeline } from "@/hooks/use-pipeline";
import { useRealtimeStatus } from "@/hooks/use-realtime";
import { cn } from "@/lib/utils";
import type { Lead } from "@/types";

interface ActiveCard {
  lead: Lead;
  stageColor?: string;
}

function LiveIndicator() {
  const status = useRealtimeStatus();

  return (
    <div
      className={cn(
        "flex items-center gap-1.5 text-[11px] font-medium px-2 py-0.5 rounded-full border transition-all duration-500",
        status === "connected"
          ? "text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-900/20"
          : status === "connecting"
          ? "text-amber-500 border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/20"
          : "text-muted-foreground border-border bg-muted/40",
      )}
    >
      {status === "connected" ? (
        <>
          <span className="relative flex h-1.5 w-1.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-60" />
            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500" />
          </span>
          Ao vivo
        </>
      ) : status === "connecting" ? (
        <>
          <RefreshCw className="h-3 w-3 animate-spin" />
          Conectando…
        </>
      ) : (
        <>
          <WifiOff className="h-3 w-3" />
          Offline
        </>
      )}
    </div>
  );
}

export function PipelineBoard() {
  const {
    columns,
    isLoading,
    isError,
    refetch,
    moveLead,
    isMoving,
    totalLeads,
    totalValue,
    wonLeads,
    flashIds,
    flashStageIds,
  } = usePipeline();

  const [activeCard, setActiveCard] = useState<ActiveCard | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
    useSensor(TouchSensor, { activationConstraint: { delay: 200, tolerance: 8 } }),
  );

  const handleDragStart = useCallback((event: DragStartEvent) => {
    const data = event.active.data.current as { lead: Lead; stageColor?: string } | undefined;
    if (data?.lead) setActiveCard({ lead: data.lead, stageColor: data.stageColor });
  }, []);

  const handleDragEnd = useCallback(
    (event: DragEndEvent) => {
      const { active, over } = event;
      setActiveCard(null);
      if (!over) return;

      const leadId = Number((active.id as string).replace("card-", ""));
      const targetStageId = Number((over.id as string).replace("col-", ""));
      if (isNaN(leadId) || isNaN(targetStageId)) return;

      const currentStageId = columns
        .flatMap((c) => c.leads)
        .find((l) => l.id === leadId)?.stage_id;

      if (currentStageId !== targetStageId) {
        moveLead({ leadId, stageId: targetStageId });
      }
    },
    [columns, moveLead],
  );

  const handleDragCancel = useCallback(() => setActiveCard(null), []);

  if (isLoading) return <PipelineSkeleton />;

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <AlertCircle className="h-10 w-10 text-destructive" />
        <p className="text-muted-foreground font-medium">Erro ao carregar o pipeline</p>
        <Button variant="outline" size="sm" onClick={() => refetch()}>
          <RefreshCw className="h-4 w-4" />
          Tentar novamente
        </Button>
      </div>
    );
  }

  if (columns.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3 border-2 border-dashed border-border rounded-xl bg-muted/20">
        <Inbox className="h-10 w-10 text-muted-foreground/40" />
        <p className="text-muted-foreground font-medium">Nenhum estágio configurado</p>
        <p className="text-sm text-muted-foreground">Configure o pipeline em Configurações</p>
      </div>
    );
  }

  return (
    <DndContext
      sensors={sensors}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragCancel={handleDragCancel}
    >
      <div className="space-y-5">
        <div className="space-y-2">
          <div className="flex justify-end">
            <LiveIndicator />
          </div>
          <PipelineHeader
            totalLeads={totalLeads}
            totalValue={totalValue}
            stageCount={columns.length}
            wonLeads={wonLeads}
          />
        </div>

        {/* Indicador de movimentação */}
        <AnimatePresence>
          {isMoving && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="flex items-center gap-2 text-xs text-muted-foreground overflow-hidden"
            >
              <RefreshCw className="h-3 w-3 animate-spin" />
              Movendo lead...
            </motion.div>
          )}
        </AnimatePresence>

        {/* Board com scroll horizontal */}
        <div className="flex gap-4 overflow-x-auto pb-4 -mx-6 px-6 scrollbar-thin">
          {columns.map((column) => (
            <PipelineColumn
              key={column.stage.id}
              column={column}
              isAnyDragging={!!activeCard}
              flashIds={flashIds}
              isStageFlashing={flashStageIds.has(column.stage.id)}
            />
          ))}
        </div>
      </div>

      {/* Card flutuante durante drag */}
      <DragOverlay
        dropAnimation={{ duration: 150, easing: "cubic-bezier(0.18, 0.67, 0.6, 1.22)" }}
      >
        {activeCard && (
          <div className="w-[260px]">
            <PipelineCardDisplay
              lead={activeCard.lead}
              stageColor={activeCard.stageColor}
              isOverlay
            />
          </div>
        )}
      </DragOverlay>
    </DndContext>
  );
}
