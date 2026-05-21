"""
Channel constants and event envelope builders for the realtime system.
"""
from typing import Any

PIPELINE_UPDATES = "pipeline_updates"
TASK_UPDATES = "task_updates"
INBOX_UPDATES = "inbox_updates"
NOTIFICATIONS = "notifications"


def make_event(channel: str, event: str, payload: Any) -> dict:
    """Build a typed event envelope sent over WebSocket."""
    return {"channel": channel, "event": event, "payload": payload}


# Pipeline channel events
def lead_created_event(lead: dict) -> dict:
    return make_event(PIPELINE_UPDATES, "lead.created", lead)


def lead_moved_event(lead_id: int, from_stage: str, to_stage: str, lead: dict) -> dict:
    return make_event(PIPELINE_UPDATES, "lead.moved", {
        "lead_id": lead_id,
        "from_stage": from_stage,
        "to_stage": to_stage,
        "lead": lead,
    })


def lead_updated_event(lead: dict) -> dict:
    return make_event(PIPELINE_UPDATES, "lead.updated", lead)


# Task channel events
def task_created_event(task: dict) -> dict:
    return make_event(TASK_UPDATES, "task.created", task)


def task_updated_event(task: dict) -> dict:
    return make_event(TASK_UPDATES, "task.updated", task)


# Inbox channel events
def message_sent_event(conversation_id: int, message: dict) -> dict:
    return make_event(INBOX_UPDATES, "message.sent", {
        "conversation_id": conversation_id,
        "message": message,
    })


def message_received_event(conversation_id: int, message: dict) -> dict:
    return make_event(INBOX_UPDATES, "message.received", {
        "conversation_id": conversation_id,
        "message": message,
    })


# Notification channel events
def notification_event(notification: dict) -> dict:
    return make_event(NOTIFICATIONS, "notification.new", notification)
