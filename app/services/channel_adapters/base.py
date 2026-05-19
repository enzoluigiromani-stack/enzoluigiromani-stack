"""
Contrato base para adaptadores de canal de comunicação.

Cada canal (WhatsApp, Email, SMS) implementa esta interface.
O dispatch é síncrono e roda em BackgroundTask para não bloquear a API.

Upgrade para realtime/async:
  Substituir `send()` por `async def send()` e usar FastAPI WebSocket
  para notificar clientes conectados sobre novas mensagens recebidas.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SendResult:
    success:             bool
    external_message_id: str | None = None
    error:               str | None = None
    raw_response:        dict | None = None


class BaseChannelAdapter(ABC):
    CHANNEL: str = "unknown"

    @abstractmethod
    def send(self, to: str, content: str, message_type: str = "text", **kwargs) -> SendResult:
        """
        Envia uma mensagem pelo canal.

        Args:
            to:           destinatário (número de telefone, e-mail, etc.)
            content:      corpo da mensagem
            message_type: text | image | file
            **kwargs:     dados extras específicos do canal (subject, media_url, etc.)

        Returns:
            SendResult com sucesso/falha e ID externo gerado.
        """
        ...

    def is_configured(self) -> bool:
        """Retorna True se as credenciais do canal estão configuradas."""
        return True

    def supports_type(self, message_type: str) -> bool:
        return message_type == "text"
