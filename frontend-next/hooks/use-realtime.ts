"use client";

import { useEffect, useRef, useState } from "react";
import { useAuthStore } from "@/store/auth.store";
import { realtimeClient, WSEvent, ConnectionStatus } from "@/services/websocket.service";

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
  }, [token, user?.workspace_id]);

  useEffect(() => {
    if (!handler) return;
    const off = realtimeClient.on(handler);
    return off;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [handler, ...deps]);
}

export function useRealtimeStatus(): ConnectionStatus {
  const [status, setStatus] = useState<ConnectionStatus>(realtimeClient.status);

  useEffect(() => {
    setStatus(realtimeClient.status);
    const off = realtimeClient.onStatus(setStatus);
    return off;
  }, []);

  return status;
}
