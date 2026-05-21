import { useCallback, useEffect, useRef, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { leadsService } from "@/services/leads.service";
import { realtimeClient } from "@/services/websocket.service";
import type { KanbanColumn, Lead } from "@/types";

export const BOARD_QUERY_KEY = ["board"] as const;

// How long (ms) a card stays highlighted after arriving via WS
const HIGHLIGHT_TTL = 4000;

export function usePipeline() {
  const queryClient = useQueryClient();

  // IDs of leads that just arrived / moved via realtime — used for card highlight
  const [flashIds, setFlashIds] = useState<Set<number>>(new Set());
  const flashTimers = useRef<Map<number, ReturnType<typeof setTimeout>>>(new Map());

  const flash = useCallback((id: number) => {
    setFlashIds((prev) => new Set(prev).add(id));
    if (flashTimers.current.has(id)) clearTimeout(flashTimers.current.get(id));
    flashTimers.current.set(
      id,
      setTimeout(() => {
        setFlashIds((prev) => {
          const next = new Set(prev);
          next.delete(id);
          return next;
        });
        flashTimers.current.delete(id);
      }, HIGHLIGHT_TTL),
    );
  }, []);

  const { data: columns = [], isLoading, isError, refetch } = useQuery<KanbanColumn[]>({
    queryKey: BOARD_QUERY_KEY,
    queryFn: leadsService.getBoard,
    staleTime: 30_000,
    // Longer fallback interval — WS handles live updates
    refetchInterval: 300_000,
  });

  // ── Apply realtime events to the board cache ───────────────────────────────
  useEffect(() => {
    const off = realtimeClient.on((event) => {
      if (event.channel !== "pipeline_updates") return;

      if (event.event === "lead.created") {
        const lead = event.payload as Lead;
        queryClient.setQueryData<KanbanColumn[]>(BOARD_QUERY_KEY, (old = []) => {
          // Skip if already present (own optimistic insert or duplicate)
          const exists = old.some((col) => col.leads.some((l) => l.id === lead.id));
          if (exists) return old;

          return old.map((col) =>
            col.stage.id === lead.stage_id
              ? { ...col, leads: [lead, ...col.leads] }
              : col,
          );
        });
        flash(lead.id);
      }

      if (event.event === "lead.moved") {
        const { lead_id, lead } = event.payload as {
          lead_id: number;
          from_stage: string;
          to_stage: string;
          lead: Lead;
        };
        queryClient.setQueryData<KanbanColumn[]>(BOARD_QUERY_KEY, (old = []) =>
          old.map((col) => {
            // Remove from every column first, then insert into target
            const withoutLead = col.leads.filter((l) => l.id !== lead_id);
            if (col.stage.id === lead.stage_id) {
              return { ...col, leads: [lead, ...withoutLead] };
            }
            return { ...col, leads: withoutLead };
          }),
        );
        flash(lead_id);
      }

      if (event.event === "lead.updated") {
        const lead = event.payload as Lead;
        queryClient.setQueryData<KanbanColumn[]>(BOARD_QUERY_KEY, (old = []) =>
          old.map((col) => ({
            ...col,
            leads: col.leads.map((l) => (l.id === lead.id ? { ...l, ...lead } : l)),
          })),
        );
      }
    });

    return off;
  }, [queryClient, flash]);

  // ── Drag-and-drop mutation with optimistic update ──────────────────────────
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
  };
}
