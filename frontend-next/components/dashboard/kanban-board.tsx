"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { GripVertical, DollarSign, User } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { leadsService } from "@/services/leads.service";
import { cn } from "@/lib/utils";
import type { KanbanColumn, Lead } from "@/types";

const CHANNEL_COLORS: Record<string, string> = {
  facebook: "bg-blue-100 text-blue-700",
  google: "bg-red-100 text-red-700",
  organic: "bg-green-100 text-green-700",
  high_ticket: "bg-purple-100 text-purple-700",
};

function LeadCard({ lead, onDragStart }: { lead: Lead; onDragStart: () => void }) {
  return (
    <div
      draggable
      onDragStart={onDragStart}
      className="cursor-grab active:cursor-grabbing"
    >
      <Card className="p-3 space-y-2 hover:shadow-md transition-all border-l-4 border-l-primary/30 hover:border-l-primary">
        <div className="flex items-start justify-between gap-2">
          <p className="text-sm font-medium leading-tight line-clamp-2">{lead.name}</p>
          <GripVertical className="h-4 w-4 text-muted-foreground shrink-0 mt-0.5" />
        </div>

        {lead.company && (
          <p className="text-xs text-muted-foreground flex items-center gap-1">
            <User className="h-3 w-3" />
            {lead.company}
          </p>
        )}

        {lead.value && (
          <p className="text-xs font-medium text-green-600 flex items-center gap-1">
            <DollarSign className="h-3 w-3" />
            {lead.value.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}
          </p>
        )}

        {lead.tags && lead.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {lead.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className={cn(
                  "px-1.5 py-0.5 rounded-full text-[10px] font-medium",
                  CHANNEL_COLORS[tag] ?? "bg-secondary text-secondary-foreground"
                )}
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

interface KanbanBoardProps {
  columns: KanbanColumn[];
}

export function KanbanBoard({ columns }: KanbanBoardProps) {
  const queryClient = useQueryClient();
  const [dragging, setDragging] = useState<{ leadId: number; fromStageId: number } | null>(null);
  const [dragOverStage, setDragOverStage] = useState<number | null>(null);

  const moveMutation = useMutation({
    mutationFn: ({ leadId, stageId }: { leadId: number; stageId: number }) =>
      leadsService.moveLead(leadId, stageId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["board"] }),
  });

  function handleDrop(stageId: number) {
    if (!dragging || dragging.fromStageId === stageId) return;
    moveMutation.mutate({ leadId: dragging.leadId, stageId });
    setDragging(null);
    setDragOverStage(null);
  }

  return (
    <div className="flex gap-4 overflow-x-auto pb-4">
      {columns.map(({ stage, leads }) => (
        <div
          key={stage.id}
          className={cn(
            "flex flex-col gap-3 min-w-[280px] max-w-[280px] rounded-lg p-3 transition-colors",
            dragOverStage === stage.id ? "bg-accent" : "bg-muted/50"
          )}
          onDragOver={(e) => { e.preventDefault(); setDragOverStage(stage.id); }}
          onDragLeave={() => setDragOverStage(null)}
          onDrop={() => handleDrop(stage.id)}
        >
          {/* Column header */}
          <div className="flex items-center justify-between px-1">
            <div className="flex items-center gap-2">
              <div
                className="h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: stage.color ?? "#6366f1" }}
              />
              <span className="text-sm font-semibold">{stage.name}</span>
            </div>
            <Badge variant="secondary" className="text-xs">
              {leads.length}
            </Badge>
          </div>

          {/* Cards */}
          <div className="flex flex-col gap-2 flex-1 min-h-[200px]">
            {leads.map((lead) => (
              <LeadCard
                key={lead.id}
                lead={lead}
                onDragStart={() => setDragging({ leadId: lead.id, fromStageId: stage.id })}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
