"use client";

/**
 * Mounts once in the dashboard layout.
 * Subscribes to ALL WS channels and keeps React Query caches in sync
 * so every page (dashboard, pipeline, tasks, inbox) sees live data
 * without each page needing its own subscription.
 */

import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { realtimeClient } from "@/services/websocket.service";
import { BOARD_QUERY_KEY } from "@/hooks/use-pipeline";
import type { KanbanColumn, Lead, Task, Message, Conversation } from "@/types";

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
          // Insert into flat leads list without a full refetch
          queryClient.setQueryData<Lead[]>(["leads"], (old) => {
            if (!old) return old;
            if (old.some((l) => l.id === lead.id)) return old;
            return [lead, ...old];
          });
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
          // Update flat leads list in place
          queryClient.setQueryData<Lead[]>(["leads"], (old) => {
            if (!old) return old;
            return old.map((l) => (l.id === lead.id ? { ...l, ...lead } : l));
          });
        }
      }

      // ── Tasks → update all matching caches + summary ─────────────────────
      if (event.channel === "task_updates") {
        if (event.event === "task.created") {
          const task = event.payload as Task;
          // Insert into each active tasks cache where the filter matches
          queryClient
            .getQueriesData<Task[]>({ queryKey: ["tasks"] })
            .forEach(([key, data]) => {
              if (!data) return;
              const filter = key[1] as string | undefined;
              const matches = !filter || filter === task.status;
              if (matches && !data.some((t) => t.id === task.id)) {
                queryClient.setQueryData<Task[]>(key, [task, ...data]);
              }
            });
          queryClient.invalidateQueries({ queryKey: ["task-summary"] });
        }

        if (event.event === "task.updated") {
          const task = event.payload as Task;
          queryClient
            .getQueriesData<Task[]>({ queryKey: ["tasks"] })
            .forEach(([key, data]) => {
              if (!data) return;
              const filter = key[1] as string | undefined;
              const exists = data.some((t) => t.id === task.id);
              const shouldBeHere = !filter || filter === task.status;

              if (exists && shouldBeHere) {
                queryClient.setQueryData<Task[]>(
                  key,
                  data.map((t) => (t.id === task.id ? { ...t, ...task } : t)),
                );
              } else if (exists && !shouldBeHere) {
                // Status changed away from this filter — remove
                queryClient.setQueryData<Task[]>(
                  key,
                  data.filter((t) => t.id !== task.id),
                );
              } else if (!exists && shouldBeHere) {
                queryClient.setQueryData<Task[]>(key, [task, ...data]);
              }
            });
          queryClient.invalidateQueries({ queryKey: ["task-summary"] });
        }
      }

      // ── Inbox → message + conversation caches ───────────────────────────
      if (event.channel === "inbox_updates") {
        const { conversation_id, message } = event.payload as {
          conversation_id: number;
          message: Message;
        };

        // Append to message cache if it's already loaded
        queryClient.setQueryData<Message[]>(
          ["messages", conversation_id],
          (old) => {
            if (!old) return old;
            if (old.some((m) => m.id === message.id)) return old;
            return [...old.filter((m) => !m._optimistic), message];
          },
        );

        // Bump last_message_at and re-sort conversations list
        queryClient.setQueryData<Conversation[]>(["conversations"], (old = []) => {
          const updated = old.map((c) =>
            c.id === conversation_id
              ? { ...c, last_message_at: message.created_at }
              : c,
          );
          return [...updated].sort((a, b) => {
            const at = a.last_message_at ?? a.created_at;
            const bt = b.last_message_at ?? b.created_at;
            return new Date(bt).getTime() - new Date(at).getTime();
          });
        });
      }
    });

    return off;
  }, [queryClient]);

  return null;
}
