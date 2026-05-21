"use client";

import { useCallback, useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { realtimeClient } from "@/services/websocket.service";
import { inboxService } from "@/services/inbox.service";
import type { Conversation, Message } from "@/types";

export const CONVS_KEY = ["conversations"] as const;
export const MSGS_KEY = (id: number) => ["messages", id] as const;

export function useInbox(selectedId: number | null) {
  const queryClient = useQueryClient();
  const [unreadIds, setUnreadIds] = useState<Set<number>>(new Set());

  const { data: conversations = [], isLoading } = useQuery<Conversation[]>({
    queryKey: CONVS_KEY,
    queryFn: inboxService.getConversations,
    staleTime: 30_000,
    refetchInterval: 300_000,
  });

  const markRead = useCallback((id: number) => {
    setUnreadIds((prev) => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
  }, []);

  // Apply WS events to conversations + message caches
  useEffect(() => {
    const off = realtimeClient.on((event) => {
      if (event.channel !== "inbox_updates") return;

      const payload = event.payload as {
        conversation_id: number;
        message: Message;
      };
      const { conversation_id, message } = payload;

      // Append to message cache if loaded (avoid duplicates)
      queryClient.setQueryData<Message[]>(MSGS_KEY(conversation_id), (old) => {
        if (!old) return old; // don't create cache for conversations not open
        if (old.some((m) => m.id === message.id)) return old;
        return [...old.filter((m) => !m._optimistic || m.id !== message.id), message];
      });

      // Bump conversation last_message_at + re-sort
      queryClient.setQueryData<Conversation[]>(CONVS_KEY, (old = []) => {
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

      // Mark unread if not the active conversation
      if (conversation_id !== selectedId) {
        setUnreadIds((prev) => new Set(prev).add(conversation_id));
      }
    });

    return off;
  }, [queryClient, selectedId]);

  return { conversations, isLoading, unreadIds, markRead };
}
