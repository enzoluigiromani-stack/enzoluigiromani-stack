"""
Helper functions to broadcast realtime events.
These are called from BackgroundTasks in API routes so they don't block the response.
"""
import asyncio
import logging

from app.websocket.connection_manager import manager, get_main_loop
from app.websocket import channels

logger = logging.getLogger(__name__)


def _run(coro):
    """
    Schedule a coroutine onto the main event loop from any thread context.
    BackgroundTasks for sync routes run in a thread pool, so we must use
    run_coroutine_threadsafe instead of ensure_future (which is not thread-safe).
    """
    loop = get_main_loop()
    if loop and loop.is_running():
        asyncio.run_coroutine_threadsafe(coro, loop)
    else:
        # Fallback: direct async run (e.g. tests or CLI usage)
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


def broadcast_lead_deleted(workspace_id: int, lead_id: int):
    _run(manager.broadcast_workspace(workspace_id, channels.lead_deleted_event(lead_id)))


def broadcast_task_created(workspace_id: int, task: dict):
    _run(manager.broadcast_workspace(workspace_id, channels.task_created_event(task)))


def broadcast_task_updated(workspace_id: int, task: dict):
    _run(manager.broadcast_workspace(workspace_id, channels.task_updated_event(task)))


def broadcast_conversation_created(workspace_id: int, conversation: dict):
    _run(manager.broadcast_workspace(workspace_id, channels.conversation_created_event(conversation)))


def broadcast_conversation_updated(workspace_id: int, conversation: dict):
    _run(manager.broadcast_workspace(workspace_id, channels.conversation_updated_event(conversation)))


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


def broadcast_stage_created(workspace_id: int, stage: dict):
    _run(manager.broadcast_workspace(workspace_id, channels.stage_created_event(stage)))


def broadcast_stage_updated(workspace_id: int, stage: dict):
    _run(manager.broadcast_workspace(workspace_id, channels.stage_updated_event(stage)))


def broadcast_stage_deleted(workspace_id: int, stage_id: int):
    _run(manager.broadcast_workspace(workspace_id, channels.stage_deleted_event(stage_id)))


def broadcast_member_invited(workspace_id: int, member: dict):
    _run(manager.broadcast_workspace(workspace_id, channels.member_invited_event(member)))


def broadcast_member_updated(workspace_id: int, member: dict):
    _run(manager.broadcast_workspace(workspace_id, channels.member_updated_event(member)))


def broadcast_member_removed(workspace_id: int, member_id: int):
    _run(manager.broadcast_workspace(workspace_id, channels.member_removed_event(member_id)))
