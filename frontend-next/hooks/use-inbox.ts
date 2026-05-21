"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { realtimeClient } from "@/services/websocket.service";
import { inboxService } from "@/services/inbox.service";
import type { Conversation, Message } from "@/types";

export const CONVS_KEY = ["conversations"] as const;
export const MSGS_KEY = (id: number) => ["messages", id] as const;

const FLASH_TTL = 3000;

export function useInbox(selectedId: number | null) {
  const queryClient = useQueryClient();
  const [unreadIds, setUnreadIds] = useState<Set<number>>(new Set());
  const [flashConvIds, setFlashConvIds] = useState<Set<number>>(new Set());
  const flashTimers = useRef<Map<number, ReturnType<typeof setTimeout>>>(new Map());

  const { data: conversations = [], isLoading } = useQuery<Conversation[]>({
    queryKey: CONVS_KEY,
    queryFn: inboxService.getConversations,
    staleTime: 30_000,
    refetchInterval: 300_000,
  });

  const markRead = useCallback((id: number) => {
    setUnreadIds((prev) => { const n = new Set(prev); n.delete(id); return n; });
  }, []);

  const flashConv = useCallback((id: number) => {
    setFlashConvIds((prev) => new Set(prev).add(id));
    if (flashTimers.current.has(id)) clearTimeout(flashTimers.current.get(id));
    flashTimers.current.set(
      id,
      setTimeout(() => {
        setFlashConvIds((prev) => { const n = new Set(prev); n.delete(id); return n; });
        flashTimers.current.delete(id);
      }, FLASH_TTL),
    );
  }, []);

  // Track unread + flash — cache updates handled by RealtimeSync
  useEffect(() => {
    const off = realtimeClient.on((event) => {
      if (event.channel !== "inbox_updates") return;
      if (event.event !== "message.sent" && event.event !== "message.received") return;
      const { conversation_id } = event.payload as { conversation_id: number; message: Message };
      if (conversation_id !== selectedId) {
        setUnreadIds((prev) => new Set(prev).add(conversation_id));
      }
      flashConv(conversation_id);
    });
    return off;
  }, [selectedId, flashConv]);

  return { conversations, isLoading, unreadIds, flashConvIds, markRead };
}
