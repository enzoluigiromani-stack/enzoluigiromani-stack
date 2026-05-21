"use client";

/**
 * Mounts once in the dashboard layout.
 * Subscribes to ALL WS channels and keeps React Query caches in sync
 * so every page (dashboard, pipeline, tasks) sees live data without
 * each page needing its own subscription.
 */

import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { realtimeClient } from "@/services/websocket.service";
import { BOARD_QUERY_KEY } from "@/hooks/use-pipeline";
import type { KanbanColumn, Lead } from "@/types";

export function RealtimeSync() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const off = realtimeClient.on((event) => {

      // ── Pipeline → board cache ───────────────────────────────────────────
      if (event.channel === "pipeline_updates") {
        if (event.event === "lead.created") {
          const lead = event.payload as Lead;
          queryClient.setQueryData<KanbanColumn[]>(BOARD_QUERY_KEY, (old = []) => {
            if (old.some((col) => col.leads.some((l) => l.id === lead.id))) return old;
            return old.map((col) =>
              col.stage.id === lead.stage_id
                ? { ...col, leads: [lead, ...col.leads] }
                : col,
            );
          });
          queryClient.invalidateQueries({ queryKey: ["leads"] });
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
              const without = col.leads.filter((l) => l.id !== lead_id);
              return col.stage.id === lead.stage_id
                ? { ...col, leads: [lead, ...without] }
                : { ...col, leads: without };
            }),
          );
        }

        if (event.event === "lead.updated") {
          const lead = event.payload as Lead;
          queryClient.setQueryData<KanbanColumn[]>(BOARD_QUERY_KEY, (old = []) =>
            old.map((col) => ({
              ...col,
              leads: col.leads.map((l) => (l.id === lead.id ? { ...l, ...lead } : l)),
            })),
          );
          queryClient.invalidateQueries({ queryKey: ["leads"] });
        }
      }

      // ── Tasks → invalidate summary ───────────────────────────────────────
      if (event.channel === "task_updates") {
        queryClient.invalidateQueries({ queryKey: ["task-summary"] });
        queryClient.invalidateQueries({ queryKey: ["tasks"] });
      }
    });

    return off;
  }, [queryClient]);

  return null;
}
