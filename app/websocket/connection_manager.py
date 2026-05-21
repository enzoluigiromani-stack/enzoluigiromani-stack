import asyncio
import logging
from collections import defaultdict
from typing import Dict, List

from fastapi import WebSocket

logger = logging.getLogger(__name__)

_main_loop: asyncio.AbstractEventLoop | None = None


def set_main_loop(loop: asyncio.AbstractEventLoop) -> None:
    global _main_loop
    _main_loop = loop


def get_main_loop() -> asyncio.AbstractEventLoop | None:
    return _main_loop


class ConnectionManager:
    """
    Manages active WebSocket connections with multi-tenant isolation.
    Connections are tracked by workspace_id and user_id.
    Prepared for Redis pubsub via broadcast_workspace/broadcast_user stubs.
    """

    def __init__(self):
        # workspace_id -> list of WebSockets
        self._workspace: Dict[int, List[WebSocket]] = defaultdict(list)
        # user_id -> list of WebSockets (same user, multiple tabs)
        self._user: Dict[int, List[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, workspace_id: int, user_id: int):
        await websocket.accept()
        self._workspace[workspace_id].append(websocket)
        self._user[user_id].append(websocket)
        logger.info("WS connected: workspace=%s user=%s total=%s",
                    workspace_id, user_id,
                    sum(len(v) for v in self._workspace.values()))

    def disconnect(self, websocket: WebSocket, workspace_id: int, user_id: int):
        if websocket in self._workspace[workspace_id]:
            self._workspace[workspace_id].remove(websocket)
        if websocket in self._user[user_id]:
            self._user[user_id].remove(websocket)
        logger.info("WS disconnected: workspace=%s user=%s", workspace_id, user_id)

    async def broadcast_workspace(self, workspace_id: int, message: dict):
        """Send message to all connections in a workspace."""
        # Future: publish to Redis channel f"ws:workspace:{workspace_id}"
        dead = []
        for ws in list(self._workspace.get(workspace_id, [])):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            if ws in self._workspace[workspace_id]:
                self._workspace[workspace_id].remove(ws)

    async def broadcast_user(self, user_id: int, message: dict):
        """Send message to all connections of a specific user (multi-tab)."""
        # Future: publish to Redis channel f"ws:user:{user_id}"
        dead = []
        for ws in list(self._user.get(user_id, [])):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            if ws in self._user[user_id]:
                self._user[user_id].remove(ws)

    def connection_count(self, workspace_id: int) -> int:
        return len(self._workspace.get(workspace_id, []))


manager = ConnectionManager()
