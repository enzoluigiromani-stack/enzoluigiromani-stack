"""
Adaptador Email via SendGrid.

Credenciais necessárias (.env):
  SENDGRID_API_KEY
  EMAIL_FROM           # remetente verificado no SendGrid

Upgrade para SMTP genérico:
  Substituir SendGridAPIClient por smtplib.SMTP com credenciais
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS.
"""

import logging
import os

from .base import BaseChannelAdapter, SendResult

logger = logging.getLogger(__name__)

_SANDBOX = lambda: os.getenv("NOTIFICATIONS_SANDBOX", "false").lower() == "true"  # noqa: E731


class EmailAdapter(BaseChannelAdapter):
    CHANNEL = "email"

    def is_configured(self) -> bool:
        return bool(os.getenv("SENDGRID_API_KEY") and os.getenv("EMAIL_FROM"))

    def supports_type(self, message_type: str) -> bool:
        return message_type in ("text", "file")

    def send(self, to: str, content: str, message_type: str = "text", **kwargs) -> SendResult:
        subject = kwargs.get("subject", "(sem assunto)")

        if _SANDBOX():
            logger.info("[SANDBOX] E-mail → %s | %s | %s", to, subject, content[:80])
            return SendResult(success=True, external_message_id="sandbox-email-000")

        if not self.is_configured():
            logger.warning("SendGrid não configurado.")
            return SendResult(success=False, error="E-mail não configurado")

        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            html = content if "<" in content else f"<p>{content}</p>"
            msg  = Mail(
                from_email=os.getenv("EMAIL_FROM"),
                to_emails=to,
                subject=subject,
                html_content=html,
            )
            sg   = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
            resp = sg.send(msg)
            msg_id = dict(resp.headers).get("X-Message-Id", "")
            logger.info("E-mail enviado para %s | ID: %s", to, msg_id)
            return SendResult(
                success=True,
                external_message_id=msg_id,
                raw_response={"status_code": resp.status_code},
            )
        except Exception as exc:
            logger.error("Falha e-mail para %s: %s", to, exc)
            return SendResult(success=False, error=str(exc))
