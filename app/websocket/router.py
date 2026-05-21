import os
import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.user import User
from app.websocket.connection_manager import manager

router = APIRouter()
logger = logging.getLogger(__name__)


def _auth_token(token: str) -> User | None:
    """Validate JWT and return User, or None on failure."""
    db: Session = SessionLocal()
    try:
        secret = os.getenv("JWT_SECRET")
        algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        user_id = payload.get("sub")
        if not user_id:
            return None
        return db.query(User).filter(User.id == int(user_id)).first()
    except JWTError:
        return None
    finally:
        db.close()


@router.websocket("/ws/{workspace_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    workspace_id: int,
    token: str = Query(...),
):
    """
    WebSocket endpoint with JWT auth via query param.
    Browsers cannot set custom headers on WS connections, so token is in the query string.
    """
    user = _auth_token(token)
    if not user or user.workspace_id != workspace_id:
        await websocket.close(code=4001)
        logger.warning("WS auth failed: workspace=%s", workspace_id)
        return

    await manager.connect(websocket, workspace_id, user.id)
    try:
        await websocket.send_json({"event": "connected", "workspace_id": workspace_id})
        while True:
            # Keep-alive: accept pings from client (e.g. {"type":"ping"})
            data = await websocket.receive_json()
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, workspace_id, user.id)
