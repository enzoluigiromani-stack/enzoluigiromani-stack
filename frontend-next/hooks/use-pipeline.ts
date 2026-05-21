import { useCallback, useEffect, useRef, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { leadsService } from "@/services/leads.service";
import { realtimeClient } from "@/services/websocket.service";
import type { KanbanColumn, Lead, Stage } from "@/types";

export const BOARD_QUERY_KEY = ["board"] as const;

const HIGHLIGHT_TTL = 4000;

export function usePipeline() {
  const queryClient = useQueryClient();

  // Flash for lead cards
  const [flashIds, setFlashIds] = useState<Set<number>>(new Set());
  const flashTimers = useRef<Map<number, ReturnType<typeof setTimeout>>>(new Map());

  const flash = useCallback((id: number) => {
    setFlashIds((prev) => new Set(prev).add(id));
    if (flashTimers.current.has(id)) clearTimeout(flashTimers.current.get(id));
    flashTimers.current.set(
      id,
      setTimeout(() => {
        setFlashIds((prev) => { const n = new Set(prev); n.delete(id); return n; });
        flashTimers.current.delete(id);
      }, HIGHLIGHT_TTL),
    );
  }, []);

  // Flash for stage column headers
  const [flashStageIds, setFlashStageIds] = useState<Set<number>>(new Set());
  const flashStageTimers = useRef<Map<number, ReturnType<typeof setTimeout>>>(new Map());

  const flashStage = useCallback((id: number) => {
    setFlashStageIds((prev) => new Set(prev).add(id));
    if (flashStageTimers.current.has(id)) clearTimeout(flashStageTimers.current.get(id));
    flashStageTimers.current.set(
      id,
      setTimeout(() => {
        setFlashStageIds((prev) => { const n = new Set(prev); n.delete(id); return n; });
        flashStageTimers.current.delete(id);
      }, HIGHLIGHT_TTL),
    );
  }, []);

  const { data: columns = [], isLoading, isError, refetch } = useQuery<KanbanColumn[]>({
    queryKey: BOARD_QUERY_KEY,
    queryFn: leadsService.getBoard,
    staleTime: 30_000,
    refetchInterval: 300_000,
  });

  // Flash highlights only — cache updates are handled by RealtimeSync provider
  useEffect(() => {
    const off = realtimeClient.on((event) => {
      if (event.channel === "pipeline_updates") {
        if (event.event === "lead.created") flash((event.payload as Lead).id);
        if (event.event === "lead.moved") flash((event.payload as { lead_id: number }).lead_id);
        if (event.event === "lead.updated") flash((event.payload as Lead).id);
      }
      if (event.channel === "settings_updates") {
        if (event.event === "stage.created") flashStage((event.payload as Stage).id);
        if (event.event === "stage.updated") flashStage((event.payload as Stage).id);
      }
    });
    return off;
  }, [flash, flashStage]);

  // Drag-and-drop mutation with optimistic update
  const moveMutation = useMutation({
    mutationFn: ({ leadId, stageId }: { leadId: number; stageId: number }) =>
      leadsService.moveLead(leadId, stageId),

    onMutate: async ({ leadId, stageId }) => {
      await queryClient.cancelQueries({ queryKey: BOARD_QUERY_KEY });
      const previousBoard = queryClient.getQueryData<KanbanColumn[]>(BOARD_QUERY_KEY);

      queryClient.setQueryData<KanbanColumn[]>(BOARD_QUERY_KEY, (old = []) => {
        const lead = old.flatMap((c) => c.leads).find((l) => l.id === leadId);
        if (!lead) return old;
        const targetColumn = old.find((c) => c.stage.id === stageId);
        if (!targetColumn) return old;
        const updatedLead: Lead = { ...lead, stage_id: stageId, stage: targetColumn.stage };
        return old.map((col) => {
          if (col.stage.id === stageId) {
            return { ...col, leads: [...col.leads.filter((l) => l.id !== leadId), updatedLead] };
          }
          return { ...col, leads: col.leads.filter((l) => l.id !== leadId) };
        });
      });

      return { previousBoard };
    },

    onError: (_, __, context) => {
      if (context?.previousBoard) {
        queryClient.setQueryData(BOARD_QUERY_KEY, context.previousBoard);
      }
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: BOARD_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ["leads"] });
      queryClient.invalidateQueries({ queryKey: ["task-summary"] });
    },
  });

  const allLeads = columns.flatMap((c) => c.leads);
  const totalLeads = allLeads.length;
  const totalValue = allLeads.reduce((sum, l) => sum + (l.value ?? 0), 0);
  const wonLeads = allLeads.filter((l) => l.status === "won").length;

  return {
    columns,
    isLoading,
    isError,
    refetch,
    moveLead: moveMutation.mutate,
    isMoving: moveMutation.isPending,
    totalLeads,
    totalValue,
    wonLeads,
    flashIds,
    flashStageIds,
  };
}
