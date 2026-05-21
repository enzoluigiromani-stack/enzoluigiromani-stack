"use client";

import { useEffect, useState } from "react";
import { realtimeClient } from "@/services/websocket.service";

export type FeedEvent = {
  id: number;
  type: "lead_created" | "lead_moved" | "task_created" | "message_sent" | "message_received";
  title: string;
  description?: string;
  at: Date;
};

const MAX_EVENTS = 12;

let _seq = 0;
function nextId() { return ++_seq; }

export function useActivityFeed() {
  const [events, setEvents] = useState<FeedEvent[]>([]);

  useEffect(() => {
    const off = realtimeClient.on((event) => {
      let item: Omit<FeedEvent, "id" | "at"> | null = null;

      if (event.channel === "pipeline_updates") {
        if (event.event === "lead.created") {
          const p = event.payload as { name?: string; source?: string };
          item = {
            type: "lead_created",
            title: `Novo lead: ${p.name ?? "—"}`,
            description: p.source ? `via ${p.source}` : undefined,
          };
        }
        if (event.event === "lead.moved") {
          const p = event.payload as {
            lead: { name?: string };
            from_stage: string;
            to_stage: string;
          };
          item = {
            type: "lead_moved",
            title: `Lead movido: ${p.lead?.name ?? "—"}`,
            description: `${p.from_stage} → ${p.to_stage}`,
          };
        }
      }

      if (event.channel === "task_updates" && event.event === "task.created") {
        const p = event.payload as { title?: string; priority?: string };
        item = {
          type: "task_created",
          title: `Tarefa criada: ${p.title ?? "—"}`,
          description: p.priority ? `Prioridade ${p.priority}` : undefined,
        };
      }

      if (event.channel === "inbox_updates") {
        if (event.event === "message.sent") {
          const p = event.payload as { conversation_id: number };
          item = {
            type: "message_sent",
            title: "Mensagem enviada",
            description: `Conversa #${p.conversation_id}`,
          };
        }
        if (event.event === "message.received") {
          const p = event.payload as { conversation_id: number; message?: { content?: string } };
          item = {
            type: "message_received",
            title: "Mensagem recebida",
            description: p.message?.content
              ? p.message.content.slice(0, 48) + (p.message.content.length > 48 ? "…" : "")
              : `Conversa #${p.conversation_id}`,
          };
        }
      }

      if (!item) return;
      const feedEvent: FeedEvent = { ...item, id: nextId(), at: new Date() };
      setEvents((prev) => [feedEvent, ...prev].slice(0, MAX_EVENTS));
    });

    return off;
  }, []);

  return events;
}
