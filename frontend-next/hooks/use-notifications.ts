"use client";

import { useCallback, useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notificationsService, Notification } from "@/services/notifications.service";
import { realtimeClient } from "@/services/websocket.service";

export function useNotifications() {
  const qc = useQueryClient();

  const { data: notifications = [], isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => notificationsService.list(),
    staleTime: 30_000,
  });

  const unreadCount = notifications.filter((n) => !n.read).length;

  const markRead = useMutation({
    mutationFn: (id: number) => notificationsService.markRead(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notifications"] }),
  });

  const markAllRead = useMutation({
    mutationFn: () => notificationsService.markAllRead(),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notifications"] }),
  });

  // Live push via WebSocket
  useEffect(() => {
    const off = realtimeClient.on((event) => {
      if (event.channel === "notifications" && event.event === "notification.new") {
        qc.invalidateQueries({ queryKey: ["notifications"] });
      }
    });
    return off;
  }, [qc]);

  return {
    notifications,
    unreadCount,
    isLoading,
    markRead: (id: number) => markRead.mutate(id),
    markAllRead: () => markAllRead.mutate(),
  };
}
