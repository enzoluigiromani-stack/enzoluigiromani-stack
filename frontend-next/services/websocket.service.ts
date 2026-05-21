const BASE_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000")
  .replace(/^http/, "ws");

export type WSEvent = {
  channel: string;
  event: string;
  payload: unknown;
};

export type ConnectionStatus = "connecting" | "connected" | "disconnected";

type Handler = (event: WSEvent) => void;
type StatusHandler = (status: ConnectionStatus) => void;

class RealtimeClient {
  private ws: WebSocket | null = null;
  private handlers: Handler[] = [];
  private statusHandlers: StatusHandler[] = [];
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private workspaceId: number | null = null;
  private token: string | null = null;
  private stopped = false;
  private _status: ConnectionStatus = "disconnected";

  get status(): ConnectionStatus {
    return this._status;
  }

  connect(workspaceId: number, token: string) {
    this.workspaceId = workspaceId;
    this.token = token;
    this.stopped = false;
    this._open();
  }

  disconnect() {
    this.stopped = true;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.ws) {
      this.ws.onclose = null;
      this.ws.close();
      this.ws = null;
    }
    this._setStatus("disconnected");
  }

  on(handler: Handler) {
    this.handlers.push(handler);
    return () => {
      this.handlers = this.handlers.filter((h) => h !== handler);
    };
  }

  onStatus(handler: StatusHandler) {
    this.statusHandlers.push(handler);
    return () => {
      this.statusHandlers = this.statusHandlers.filter((h) => h !== handler);
    };
  }

  private _setStatus(s: ConnectionStatus) {
    this._status = s;
    this.statusHandlers.forEach((h) => h(s));
  }

  private _open() {
    if (!this.workspaceId || !this.token) return;
    this._setStatus("connecting");
    const url = `${BASE_URL}/ws/${this.workspaceId}?token=${this.token}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this._setStatus("connected");
    };

    this.ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data) as WSEvent;
        this.handlers.forEach((h) => h(data));
      } catch {
        // ignore malformed frames
      }
    };

    this.ws.onclose = () => {
      this._setStatus("disconnected");
      if (!this.stopped) {
        this.reconnectTimer = setTimeout(() => this._open(), 3000);
      }
    };

    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  sendPing() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: "ping" }));
    }
  }
}

export const realtimeClient = new RealtimeClient();
