"""
Registro de adaptadores de canal do inbox omnichannel.

Para adicionar um novo canal:
1. Crie channel_adapters/<canal>.py implementando BaseChannelAdapter
2. Instancie e adicione ao dict ADAPTERS abaixo
3. O inbox_service usará automaticamente o adaptador correto
"""

from .base          import BaseChannelAdapter, SendResult
from .whatsapp      import WhatsAppAdapter
from .email_channel import EmailAdapter
from .sms           import SMSAdapter

ADAPTERS: dict[str, BaseChannelAdapter] = {
    "whatsapp": WhatsAppAdapter(),
    "email":    EmailAdapter(),
    "sms":      SMSAdapter(),
}


def get_adapter(channel: str) -> BaseChannelAdapter | None:
    return ADAPTERS.get(channel)


SUPPORTED_CHANNELS = list(ADAPTERS.keys())

__all__ = [
    "ADAPTERS",
    "SUPPORTED_CHANNELS",
    "get_adapter",
    "BaseChannelAdapter",
    "SendResult",
    "WhatsAppAdapter",
    "EmailAdapter",
    "SMSAdapter",
]
