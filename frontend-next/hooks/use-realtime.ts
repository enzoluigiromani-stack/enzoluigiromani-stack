"use client";

import { useEffect, useRef } from "react";
import { useAuthStore } from "@/store/auth.store";
import { realtimeClient, WSEvent } from "@/services/websocket.service";

/**
 * Connects to the backend WebSocket for the current user's workspace.
 * Returns a function to register an event handler.
 */
export function useRealtime(
  handler?: (event: WSEvent) => void,
  deps: unknown[] = [],
) {
  const { token, user } = useAuthStore();
  const connected = useRef(false);

  useEffect(() => {
    if (!token || !user?.workspace_id) return;
    if (!connected.current) {
      realtimeClient.connect(user.workspace_id, token);
      connected.current = true;
    }
    return () => {
      // Keep connection alive while any component is mounted.
      // Disconnect only happens on logout (handled in auth store).
    };
  }, [token, user?.workspace_id]);

  useEffect(() => {
    if (!handler) return;
    const off = realtimeClient.on(handler);
    return off;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [handler, ...deps]);
}
