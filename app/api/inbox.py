"""
Endpoints do inbox omnichannel.

POST /inbox/conversations                    Abre uma conversa
GET  /inbox/conversations                    Lista conversas (filtros: status, channel, lead_id)
GET  /inbox/conversations/{id}               Detalhes da conversa
PATCH /inbox/conversations/{id}              Fechar ou reatribuir
POST  /inbox/messages                        Envia mensagem (despacha ao canal externo em bg)
GET   /inbox/messages/{conversation_id}      Lista mensagens de uma conversa

Preparado para WebSocket:
  Adicionar GET /inbox/ws/{workspace_id} com FastAPI WebSocket
  e registrar subscriber via inbox_service.subscribe() para fazer
  push de eventos a clientes conectados.
"""

import math
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.conversation import (
    ConversationCreate, ConversationResponse, ConversationUpdate,
    PaginatedConversations,
)
from app.schemas.message import MessageCreate, MessageResponse, PaginatedMessages
from app.services import inbox_service
from app.services.channel_adapters import SUPPORTED_CHANNELS
from app.services.permissions import require_manager, require_sales
from app.services.workspace import require_workspace

router = APIRouter(prefix="/inbox", tags=["inbox"])


# ── Conversas ─────────────────────────────────────────────────────────────────

@router.post("/conversations", response_model=ConversationResponse, status_code=201)
def create_conversation(
    body: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    """Abre uma nova conversa para um lead em um canal específico."""
    if body.channel not in SUPPORTED_CHANNELS:
        raise HTTPException(
            status_code=422,
            detail=f"Canal inválido. Suportados: {SUPPORTED_CHANNELS}",
        )
    conv = inbox_service.create_conversation(
        db,
        workspace_id     = workspace.id,
        channel          = body.channel,
        lead_id          = body.lead_id,
        subject          = body.subject,
        assigned_user_id = body.assigned_user_id,
        user_id          = current_user.id,
    )
    return conv


@router.get("/conversations", response_model=PaginatedConversations)
def list_conversations(
    page:             int           = Query(1, ge=1),
    limit:            int           = Query(50, ge=1, le=200),
    status:           Optional[str] = Query(None, description="open | closed"),
    channel:          Optional[str] = Query(None),
    lead_id:          Optional[int] = Query(None),
    assigned_user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    items, total = inbox_service.get_conversations(
        db,
        workspace.id,
        status           = status,
        channel          = channel,
        lead_id          = lead_id,
        assigned_user_id = assigned_user_id,
        page             = page,
        limit            = limit,
    )
    enriched = []
    for conv in items:
        r = ConversationResponse.model_validate(conv)
        if conv.lead:
            r.lead_name  = conv.lead.name
            r.lead_email = conv.lead.email
            r.lead_phone = conv.lead.phone
        enriched.append(r)
    return PaginatedConversations(
        items = enriched,
        total = total,
        page  = page,
        limit = limit,
        pages = math.ceil(total / limit) if total else 1,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    conv = inbox_service.get_conversation(db, conversation_id, workspace.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    r = ConversationResponse.model_validate(conv)
    if conv.lead:
        r.lead_name  = conv.lead.name
        r.lead_email = conv.lead.email
        r.lead_phone = conv.lead.phone
    return r


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    conversation_id: int,
    body: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
    workspace: Workspace = Depends(require_workspace),
):
    """Fechar conversa ou reatribuir a outro usuário (manager+)."""
    if body.status == "closed":
        return inbox_service.close_conversation(db, conversation_id, workspace.id, current_user.id)

    if body.assigned_user_id is not None:
        return inbox_service.assign_conversation(
            db, conversation_id, workspace.id, body.assigned_user_id, current_user.id
        )

    raise HTTPException(status_code=422, detail="Nenhuma ação válida fornecida (status ou assigned_user_id).")


# ── Mensagens ─────────────────────────────────────────────────────────────────

@router.post("/messages", response_model=MessageResponse, status_code=201)
def send_message(
    body: MessageCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    """
    Envia uma mensagem em uma conversa.
    O despacho ao canal externo (Twilio/SendGrid) ocorre em background.
    """
    # Garante que a conversa pertence ao workspace
    conv = inbox_service.get_conversation(db, body.conversation_id, workspace.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    if conv.status == "closed":
        raise HTTPException(status_code=422, detail="Conversa encerrada. Reabra antes de enviar.")

    msg = inbox_service.add_message(
        db,
        conversation_id = body.conversation_id,
        workspace_id    = workspace.id,
        sender_type     = "user",
        content         = body.content,
        message_type    = body.message_type,
        sender_id       = current_user.id,
    )

    # Despacha ao canal externo sem bloquear a resposta
    background_tasks.add_task(
        inbox_service.dispatch_message,
        message_id = msg.id,
        db_factory = get_db,
    )

    return msg


@router.get("/messages/{conversation_id}", response_model=PaginatedMessages)
def list_messages(
    conversation_id: int,
    page:  int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
    workspace: Workspace = Depends(require_workspace),
):
    items, total = inbox_service.get_messages(
        db,
        conversation_id = conversation_id,
        workspace_id    = workspace.id,
        page            = page,
        limit           = limit,
    )
    return PaginatedMessages(
        items = items,
        total = total,
        page  = page,
        limit = limit,
        pages = math.ceil(total / limit) if total else 1,
    )
