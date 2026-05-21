import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { leadsService } from "@/services/leads.service";
import type { KanbanColumn, Lead } from "@/types";

export const BOARD_QUERY_KEY = ["board"] as const;

export function usePipeline() {
  const queryClient = useQueryClient();

  const { data: columns = [], isLoading, isError, refetch } = useQuery<KanbanColumn[]>({
    queryKey: BOARD_QUERY_KEY,
    queryFn: leadsService.getBoard,
    staleTime: 30_000,
    // Pronto para substituição por WebSocket subscription no futuro
    refetchInterval: 60_000,
  });

  const moveMutation = useMutation({
    mutationFn: ({ leadId, stageId }: { leadId: number; stageId: number }) =>
      leadsService.moveLead(leadId, stageId),

    onMutate: async ({ leadId, stageId }) => {
      await queryClient.cancelQueries({ queryKey: BOARD_QUERY_KEY });
      await queryClient.cancelQueries({ queryKey: ["leads"] });

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
  };
}
