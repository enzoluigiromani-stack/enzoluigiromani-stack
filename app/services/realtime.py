"""
Helper functions to broadcast realtime events.
These are called from BackgroundTasks in API routes so they don't block the response.
"""
import asyncio
import logging

from app.websocket.connection_manager import manager
from app.websocket import channels

logger = logging.getLogger(__name__)


def _run(coro):
    """Execute a coroutine from a sync context (BackgroundTasks)."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(coro)
        else:
            loop.run_until_complete(coro)
    except Exception:
        asyncio.run(coro)


def broadcast_lead_created(workspace_id: int, lead: dict):
    _run(manager.broadcast_workspace(workspace_id, channels.lead_created_event(lead)))


def broadcast_lead_moved(workspace_id: int, lead_id: int, from_stage: str, to_stage: str, lead: dict):
    _run(manager.broadcast_workspace(
        workspace_id,
        channels.lead_moved_event(lead_id, from_stage, to_stage, lead),
    ))


def broadcast_lead_updated(workspace_id: int, lead: dict):
    _run(manager.broadcast_workspace(workspace_id, channels.lead_updated_event(lead)))


def broadcast_task_created(workspace_id: int, task: dict):
    _run(manager.broadcast_workspace(workspace_id, channels.task_created_event(task)))


def broadcast_task_updated(workspace_id: int, task: dict):
    _run(manager.broadcast_workspace(workspace_id, channels.task_updated_event(task)))


def broadcast_message_sent(workspace_id: int, conversation_id: int, message: dict):
    _run(manager.broadcast_workspace(
        workspace_id,
        channels.message_sent_event(conversation_id, message),
    ))


def broadcast_message_received(workspace_id: int, conversation_id: int, message: dict):
    _run(manager.broadcast_workspace(
        workspace_id,
        channels.message_received_event(conversation_id, message),
    ))


def broadcast_notification(workspace_id: int, notification: dict, user_id: int | None = None):
    event = channels.notification_event(notification)
    if user_id:
        _run(manager.broadcast_user(user_id, event))
    else:
        _run(manager.broadcast_workspace(workspace_id, event))
