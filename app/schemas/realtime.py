"""
Schemas for WebSocket event payloads.
"""
from typing import Any
from pydantic import BaseModel


class WSEvent(BaseModel):
    channel: str
    event: str
    payload: Any
