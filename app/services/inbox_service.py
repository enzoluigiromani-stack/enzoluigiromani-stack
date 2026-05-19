"""
Serviço central do inbox omnichannel.

Responsabilidades:
  - Criar e gerenciar conversas
  - Adicionar mensagens (enviadas e recebidas)
  - Despachar mensagens para o canal correto via channel_adapters
  - Emitir eventos para o EventBus (preparado para WebSocket/realtime)

Upgrade para realtime:
  1. Substituir _event_bus por asyncio.Queue ou Redis Pub/Sub
  2. Adicionar endpoint WebSocket em /inbox/ws/{workspace_id}
  3. Cada conexão WS se inscreve via subscribe() para receber broadcasts
"""

import logging
import math
from datetime import datetime
from typing import Callable

from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.lead import Lead
from app.services.activity_service import log_activity
from app.services.channel_adapters import get_adapter

logger = logging.getLogger(__name__)


# ── EventBus (preparado para WebSocket) ──────────────────────────────────────

_subscribers: list[Callable[[str, dict], None]] = []


def subscribe(callback: Callable[[str, dict], None]) -> None:
    """Registra um subscriber para eventos do inbox (futuro WebSocket)."""
    _subscribers.append(callback)


def unsubscribe(callback: Callable[[str, dict], None]) -> None:
    _subscribers.remove(callback)


def _emit(event_type: str, data: dict) -> None:
    """Emite evento para todos os subscribers registrados."""
    for cb in _subscribers:
        try:
            cb(event_type, data)
        except Exception as exc:
            logger.warning("EventBus subscriber error: %s", exc)


# ── Conversations ─────────────────────────────────────────────────────────────

def create_conversation(
    db: Session,
    workspace_id: int,
    channel: str,
    *,
    lead_id: int | None = None,
    subject: str | None = None,
    assigned_user_id: int | None = None,
    user_id: int | None = None,
) -> Conversation:
    conv = Conversation(
        workspace_id     = workspace_id,
        lead_id          = lead_id,
        channel          = channel,
        status           = "open",
        subject          = subject,
        assigned_user_id = assigned_user_id,
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)

    log_activity(
        db,
        workspace_id=workspace_id,
        type="conversation_created",
        description=f"Conversa aberta via {channel}",
        user_id=user_id,
        lead_id=lead_id,
        meta={"conversation_id": conv.id, "channel": channel},
    )

    _emit("conversation_created", {"conversation_id": conv.id, "workspace_id": workspace_id})
    return conv


def get_conversations(
    db: Session,
    workspace_id: int,
    *,
    status: str | None = None,
    channel: str | None = None,
    lead_id: int | None = None,
    assigned_user_id: int | None = None,
    page: int = 1,
    limit: int = 50,
) -> tuple[list[Conversation], int]:
    q = db.query(Conversation).filter(Conversation.workspace_id == workspace_id)
    if status:           q = q.filter(Conversation.status == status)
    if channel:          q = q.filter(Conversation.channel == channel)
    if lead_id:          q = q.filter(Conversation.lead_id == lead_id)
    if assigned_user_id: q = q.filter(Conversation.assigned_user_id == assigned_user_id)

    total = q.count()
    items = (
        q.order_by(Conversation.last_message_at.desc().nulls_last(), Conversation.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return items, total


def get_conversation(db: Session, conversation_id: int, workspace_id: int) -> Conversation | None:
    return db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.workspace_id == workspace_id,
    ).first()


def close_conversation(
    db: Session,
    conversation_id: int,
    workspace_id: int,
    user_id: int | None = None,
) -> Conversation:
    conv = _get_or_404(db, conversation_id, workspace_id)
    conv.status     = "closed"
    conv.closed_at  = datetime.utcnow()
    conv.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(conv)

    log_activity(
        db,
        workspace_id=workspace_id,
        type="conversation_closed",
        description=f"Conversa #{conversation_id} encerrada",
        user_id=user_id,
        lead_id=conv.lead_id,
        meta={"conversation_id": conversation_id},
    )
    _emit("conversation_closed", {"conversation_id": conversation_id, "workspace_id": workspace_id})
    return conv


def assign_conversation(
    db: Session,
    conversation_id: int,
    workspace_id: int,
    assigned_user_id: int,
    user_id: int | None = None,
) -> Conversation:
    conv = _get_or_404(db, conversation_id, workspace_id)
    conv.assigned_user_id = assigned_user_id
    conv.updated_at       = datetime.utcnow()
    db.commit()
    db.refresh(conv)

    log_activity(
        db,
        workspace_id=workspace_id,
        type="conversation_assigned",
        description=f"Conversa #{conversation_id} atribuída ao usuário #{assigned_user_id}",
        user_id=user_id,
        lead_id=conv.lead_id,
        meta={"conversation_id": conversation_id, "assigned_to": assigned_user_id},
    )
    return conv


# ── Messages ──────────────────────────────────────────────────────────────────

def add_message(
    db: Session,
    conversation_id: int,
    workspace_id: int,
    sender_type: str,
    content: str,
    *,
    message_type: str = "text",
    sender_id: int | None = None,
    external_message_id: str | None = None,
    meta: dict | None = None,
) -> Message:
    conv = _get_or_404(db, conversation_id, workspace_id)

    msg = Message(
        conversation_id     = conversation_id,
        sender_type         = sender_type,
        sender_id           = sender_id,
        content             = content,
        message_type        = message_type,
        external_message_id = external_message_id,
        meta                = meta,
    )
    db.add(msg)

    conv.last_message_at = datetime.utcnow()
    conv.updated_at      = datetime.utcnow()
    db.commit()
    db.refresh(msg)

    activity_type = "message_sent" if sender_type == "user" else "message_received"
    log_activity(
        db,
        workspace_id=workspace_id,
        type=activity_type,
        description=f"Mensagem via {conv.channel}: {content[:60]}{'…' if len(content) > 60 else ''}",
        user_id=sender_id if sender_type == "user" else None,
        lead_id=conv.lead_id,
        meta={"conversation_id": conversation_id, "message_id": msg.id, "channel": conv.channel},
    )

    _emit("message_added", {
        "message_id":      msg.id,
        "conversation_id": conversation_id,
        "workspace_id":    workspace_id,
        "sender_type":     sender_type,
    })
    return msg


def get_messages(
    db: Session,
    conversation_id: int,
    workspace_id: int,
    *,
    page: int = 1,
    limit: int = 50,
) -> tuple[list[Message], int]:
    _get_or_404(db, conversation_id, workspace_id)  # garante multi-tenant

    q     = db.query(Message).filter(Message.conversation_id == conversation_id)
    total = q.count()
    items = (
        q.order_by(Message.created_at.asc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return items, total


# ── Dispatch para canal externo (roda em BackgroundTask) ──────────────────────

def dispatch_message(message_id: int, db_factory) -> None:
    """
    Envia a mensagem pelo canal externo.
    Chamado via BackgroundTasks para não bloquear a resposta HTTP.

    Args:
        message_id:  ID da mensagem a enviar
        db_factory:  callable que retorna uma Session (ex: next(get_db()))
    """
    db = next(db_factory())
    try:
        msg  = db.query(Message).filter(Message.id == message_id).first()
        if not msg:
            return

        conv = db.query(Conversation).filter(Conversation.id == msg.conversation_id).first()
        if not conv:
            return

        adapter = get_adapter(conv.channel)
        if not adapter:
            logger.warning("Canal '%s' sem adaptador configurado.", conv.channel)
            return

        # Determina o destinatário
        to = _resolve_recipient(db, conv)
        if not to:
            logger.warning("Conversa #%s sem destinatário resolvido.", conv.id)
            return

        result = adapter.send(
            to           = to,
            content      = msg.content,
            message_type = msg.message_type,
            subject      = conv.subject,
        )

        # Atualiza status de entrega
        if result.success:
            msg.external_message_id = result.external_message_id
            msg.delivered_at        = datetime.utcnow()
            msg.meta                = {**(msg.meta or {}), "delivery": result.raw_response}
        else:
            msg.meta = {**(msg.meta or {}), "delivery_error": result.error}

        db.commit()
    except Exception as exc:
        logger.exception("dispatch_message falhou para message_id=%s: %s", message_id, exc)
    finally:
        db.close()


# ── Helpers internos ──────────────────────────────────────────────────────────

def _get_or_404(db: Session, conversation_id: int, workspace_id: int) -> Conversation:
    from fastapi import HTTPException
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.workspace_id == workspace_id,
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    return conv


def _resolve_recipient(db: Session, conv: Conversation) -> str | None:
    """Retorna o endereço de destino com base no canal e no lead vinculado."""
    if not conv.lead_id:
        return None
    lead = db.query(Lead).filter(Lead.id == conv.lead_id).first()
    if not lead:
        return None
    if conv.channel in ("whatsapp", "sms"):
        return lead.phone
    if conv.channel == "email":
        return lead.email
    return None
