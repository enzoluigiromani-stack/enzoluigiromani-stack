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

  // Only track unread — cache updates are handled by RealtimeSync provider
  useEffect(() => {
    const off = realtimeClient.on((event) => {
      if (event.channel !== "inbox_updates") return;
      const { conversation_id } = event.payload as { conversation_id: number; message: Message };
      if (conversation_id !== selectedId) {
        setUnreadIds((prev) => new Set(prev).add(conversation_id));
      }
    });
    return off;
  }, [selectedId]);

  return { conversations, isLoading, unreadIds, markRead };
}
