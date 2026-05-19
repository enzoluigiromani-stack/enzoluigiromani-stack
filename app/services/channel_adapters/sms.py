"""
Adaptador SMS via Twilio.

Credenciais necessárias (.env):
  TWILIO_ACCOUNT_SID
  TWILIO_AUTH_TOKEN
  TWILIO_PHONE         # número Twilio verificado

Upgrade para outros provedores:
  - AWS SNS: usar boto3.client('sns').publish()
  - Vonage: usar vonage.Sms().send_message()
  - Infobip: chamada REST para api.infobip.com
"""

import logging
import os

from .base import BaseChannelAdapter, SendResult

logger = logging.getLogger(__name__)

_SANDBOX = lambda: os.getenv("NOTIFICATIONS_SANDBOX", "false").lower() == "true"  # noqa: E731


class SMSAdapter(BaseChannelAdapter):
    CHANNEL = "sms"

    def is_configured(self) -> bool:
        return bool(
            os.getenv("TWILIO_ACCOUNT_SID")
            and os.getenv("TWILIO_AUTH_TOKEN")
            and os.getenv("TWILIO_PHONE")
        )

    def send(self, to: str, content: str, message_type: str = "text", **kwargs) -> SendResult:
        if _SANDBOX():
            logger.info("[SANDBOX] SMS → %s | %s", to, content[:80])
            return SendResult(success=True, external_message_id="sandbox-sms-000")

        if not self.is_configured():
            logger.warning("Twilio SMS não configurado.")
            return SendResult(success=False, error="SMS não configurado")

        try:
            from twilio.rest import Client
            client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
            msg    = client.messages.create(
                body=content,
                from_=os.getenv("TWILIO_PHONE"),
                to=to,
            )
            logger.info("SMS enviado para %s | SID: %s", to, msg.sid)
            return SendResult(
                success=True,
                external_message_id=msg.sid,
                raw_response={"sid": msg.sid, "status": msg.status},
            )
        except Exception as exc:
            logger.error("Falha SMS para %s: %s", to, exc)
            return SendResult(success=False, error=str(exc))
