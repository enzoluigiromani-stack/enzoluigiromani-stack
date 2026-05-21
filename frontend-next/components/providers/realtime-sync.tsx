"use client";

/**
 * Mounts once in the dashboard layout.
 * Subscribes to ALL WS channels and keeps React Query caches in sync
 * so every page sees live data without each page needing its own subscription.
 */

import { useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { realtimeClient } from "@/services/websocket.service";
import { BOARD_QUERY_KEY } from "@/hooks/use-pipeline";
import type { KanbanColumn, Lead, Task, Message, Conversation, Stage, WorkspaceMember } from "@/types";

export function RealtimeSync() {
  const queryClient = useQueryClient();
  const analyticsTimer = useRef<ReturnType<typeof setTimeout>>();

  // Debounced analytics invalidation — avoids hammering on rapid events
  const scheduleAnalyticsInvalidation = () => {
    clearTimeout(analyticsTimer.current);
    analyticsTimer.current = setTimeout(() => {
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
    }, 5_000);
  };

  useEffect(() => {
    const off = realtimeClient.on((event) => {

      // ── Pipeline → board + flat leads caches ──────────────────────────────
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
          queryClient.setQueryData<Lead[]>(["leads"], (old) => {
            if (!old) return old;
            if (old.some((l) => l.id === lead.id)) return old;
            return [lead, ...old];
          });
          scheduleAnalyticsInvalidation();
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
          scheduleAnalyticsInvalidation();
        }

        if (event.event === "lead.updated") {
          const lead = event.payload as Lead;
          queryClient.setQueryData<KanbanColumn[]>(BOARD_QUERY_KEY, (old = []) =>
            old.map((col) => ({
              ...col,
              leads: col.leads.map((l) => (l.id === lead.id ? { ...l, ...lead } : l)),
            })),
          );
          queryClient.setQueryData<Lead[]>(["leads"], (old) => {
            if (!old) return old;
            return old.map((l) => (l.id === lead.id ? { ...l, ...lead } : l));
          });
          scheduleAnalyticsInvalidation();
        }

        if (event.event === "lead.deleted") {
          const { id } = event.payload as { id: number };
          queryClient.setQueryData<KanbanColumn[]>(BOARD_QUERY_KEY, (old = []) =>
            old.map((col) => ({ ...col, leads: col.leads.filter((l) => l.id !== id) })),
          );
          queryClient.setQueryData<Lead[]>(["leads"], (old) =>
            old ? old.filter((l) => l.id !== id) : old,
          );
          scheduleAnalyticsInvalidation();
        }
      }

      // ── Tasks → matching filter caches + summary ───────────────────────────
      if (event.channel === "task_updates") {
        if (event.event === "task.created") {
          const task = event.payload as Task;
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
          scheduleAnalyticsInvalidation();
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
                queryClient.setQueryData<Task[]>(key, data.filter((t) => t.id !== task.id));
              } else if (!exists && shouldBeHere) {
                queryClient.setQueryData<Task[]>(key, [task, ...data]);
              }
            });
          queryClient.invalidateQueries({ queryKey: ["task-summary"] });
          scheduleAnalyticsInvalidation();
        }
      }

      // ── Inbox → message + conversation caches ─────────────────────────────
      if (event.channel === "inbox_updates") {
        if (event.event === "conversation.created") {
          const conv = event.payload as Conversation;
          queryClient.setQueryData<Conversation[]>(["conversations"], (old = []) => {
            if (old.some((c) => c.id === conv.id)) return old;
            return [conv, ...old];
          });
          scheduleAnalyticsInvalidation();
        }

        if (event.event === "conversation.updated") {
          const conv = event.payload as Conversation;
          queryClient.setQueryData<Conversation[]>(["conversations"], (old = []) =>
            old.map((c) => (c.id === conv.id ? { ...c, ...conv } : c)),
          );
          scheduleAnalyticsInvalidation();
        }

        if (event.event === "message.sent" || event.event === "message.received") {
          const { conversation_id, message } = event.payload as {
            conversation_id: number;
            message: Message;
          };
          queryClient.setQueryData<Message[]>(
            ["messages", conversation_id],
            (old) => {
              if (!old) return old;
              if (old.some((m) => m.id === message.id)) return old;
              return [...old.filter((m) => !m._optimistic), message];
            },
          );
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
      }

      // ── Settings → stages + team-members caches ───────────────────────────
      if (event.channel === "settings_updates") {
        if (event.event === "stage.created") {
          const stage = event.payload as Stage;
          queryClient.setQueryData<Stage[]>(["stages"], (old) => {
            if (!old) return old;
            if (old.some((s) => s.id === stage.id)) return old;
            return [...old, stage].sort((a, b) => a.order - b.order);
          });
          queryClient.setQueryData<KanbanColumn[]>(BOARD_QUERY_KEY, (old) => {
            if (!old) return old;
            if (old.some((col) => col.stage.id === stage.id)) return old;
            return [...old, { stage, leads: [] }].sort(
              (a, b) => a.stage.order - b.stage.order,
            );
          });
        }

        if (event.event === "stage.updated") {
          const stage = event.payload as Stage;
          queryClient.setQueryData<Stage[]>(["stages"], (old) => {
            if (!old) return old;
            return old
              .map((s) => (s.id === stage.id ? { ...s, ...stage } : s))
              .sort((a, b) => a.order - b.order);
          });
          queryClient.setQueryData<KanbanColumn[]>(BOARD_QUERY_KEY, (old) => {
            if (!old) return old;
            return old
              .map((col) =>
                col.stage.id === stage.id
                  ? { ...col, stage: { ...col.stage, ...stage } }
                  : col,
              )
              .sort((a, b) => a.stage.order - b.stage.order);
          });
        }

        if (event.event === "stage.deleted") {
          const { id } = event.payload as { id: number };
          queryClient.setQueryData<Stage[]>(["stages"], (old) =>
            old ? old.filter((s) => s.id !== id) : old,
          );
          // Leads in this stage had their stage_id nulled — invalidate board
          queryClient.invalidateQueries({ queryKey: BOARD_QUERY_KEY });
        }

        if (event.event === "member.invited") {
          const member = event.payload as WorkspaceMember;
          queryClient.setQueryData<WorkspaceMember[]>(["team-members"], (old) => {
            if (!old) return old;
            if (old.some((m) => m.id === member.id)) return old;
            return [...old, member];
          });
          scheduleAnalyticsInvalidation();
        }

        if (event.event === "member.updated") {
          const member = event.payload as WorkspaceMember;
          queryClient.setQueryData<WorkspaceMember[]>(["team-members"], (old) =>
            old ? old.map((m) => (m.id === member.id ? { ...m, ...member } : m)) : old,
          );
          scheduleAnalyticsInvalidation();
        }

        if (event.event === "member.removed") {
          const { id } = event.payload as { id: number };
          queryClient.setQueryData<WorkspaceMember[]>(["team-members"], (old) =>
            old ? old.filter((m) => m.id !== id) : old,
          );
          scheduleAnalyticsInvalidation();
        }
      }
    });

    return () => {
      off();
      clearTimeout(analyticsTimer.current);
    };
  }, [queryClient]); // eslint-disable-line react-hooks/exhaustive-deps

  return null;
}
