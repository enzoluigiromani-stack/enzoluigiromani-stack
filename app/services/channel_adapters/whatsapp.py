"""
Adaptador WhatsApp via Twilio WhatsApp Business API.

Credenciais necessárias (.env):
  TWILIO_ACCOUNT_SID
  TWILIO_AUTH_TOKEN
  TWILIO_WHATSAPP_FROM   # formato: whatsapp:+14155238886

Upgrade para WhatsApp Cloud API (Meta):
  Substituir o bloco Twilio por chamada ao endpoint
  https://graph.facebook.com/v18.0/{phone_number_id}/messages
  usando WHATSAPP_CLOUD_TOKEN e WHATSAPP_PHONE_NUMBER_ID.
"""

import logging
import os

from .base import BaseChannelAdapter, SendResult

logger = logging.getLogger(__name__)

_SANDBOX = lambda: os.getenv("NOTIFICATIONS_SANDBOX", "false").lower() == "true"  # noqa: E731


class WhatsAppAdapter(BaseChannelAdapter):
    CHANNEL = "whatsapp"

    def is_configured(self) -> bool:
        return bool(
            os.getenv("TWILIO_ACCOUNT_SID")
            and os.getenv("TWILIO_AUTH_TOKEN")
            and os.getenv("TWILIO_WHATSAPP_FROM")
        )

    def supports_type(self, message_type: str) -> bool:
        return message_type in ("text", "image", "file")

    def send(self, to: str, content: str, message_type: str = "text", **kwargs) -> SendResult:
        if _SANDBOX():
            logger.info("[SANDBOX] WhatsApp → %s | %s", to, content[:80])
            return SendResult(success=True, external_message_id="sandbox-wa-000")

        if not self.is_configured():
            logger.warning("WhatsApp (Twilio) não configurado.")
            return SendResult(success=False, error="WhatsApp não configurado")

        try:
            from twilio.rest import Client
            client    = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
            from_num  = os.getenv("TWILIO_WHATSAPP_FROM")
            to_wa     = f"whatsapp:{to}" if not to.startswith("whatsapp:") else to
            media_url = [kwargs["media_url"]] if kwargs.get("media_url") else None

            msg = client.messages.create(
                body=content,
                from_=from_num,
                to=to_wa,
                media_url=media_url,
            )
            logger.info("WhatsApp enviado para %s | SID: %s", to, msg.sid)
            return SendResult(
                success=True,
                external_message_id=msg.sid,
                raw_response={"sid": msg.sid, "status": msg.status},
            )
        except Exception as exc:
            logger.error("Falha WhatsApp para %s: %s", to, exc)
            return SendResult(success=False, error=str(exc))
