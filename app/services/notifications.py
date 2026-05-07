import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client

logger = logging.getLogger(__name__)

STAGES_TO_NOTIFY = {"qualificado", "proposta", "fechado"}


def _sandbox() -> bool:
    return os.getenv("NOTIFICATIONS_SANDBOX", "false").lower() == "true"


# ── Primitivas ────────────────────────────────────────────────────────────────

def send_email(to: str, subject: str, html_body: str) -> bool:
    if _sandbox():
        logger.info("[SANDBOX] E-MAIL | Para: %s | Assunto: %s", to, subject)
        return True

    api_key    = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("EMAIL_FROM")
    if not api_key or not from_email:
        logger.warning("SendGrid não configurado — e-mail não enviado.")
        return False
    try:
        sg = SendGridAPIClient(api_key)
        msg = Mail(from_email=from_email, to_emails=to, subject=subject, html_content=html_body)
        sg.send(msg)
        logger.info("E-mail enviado para %s: %s", to, subject)
        return True
    except Exception as exc:
        logger.error("Falha ao enviar e-mail: %s", exc)
        return False


def send_sms(to: str, body: str) -> bool:
    if _sandbox():
        print(f"\n[SANDBOX] SMS")
        print(f"  Para:    {to}")
        print(f"  Mensagem: {body}\n")
        return True

    sid        = os.getenv("TWILIO_ACCOUNT_SID")
    token      = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_PHONE")
    if not all([sid, token, from_phone]):
        logger.warning("Twilio não configurado — SMS não enviado.")
        return False
    try:
        client = Client(sid, token)
        client.messages.create(body=body, from_=from_phone, to=to)
        logger.info("SMS enviado para %s", to)
        return True
    except Exception as exc:
        logger.error("Falha ao enviar SMS: %s", exc)
        return False


# ── Eventos de negócio ────────────────────────────────────────────────────────

def notify_new_lead(lead) -> None:
    """Dispara ao criar um lead novo: e-mail para a equipe + SMS de boas-vindas ao lead."""
    notify_email = os.getenv("NOTIFY_EMAIL", "equipe@agencia.com")
    send_email(
        to=notify_email,
        subject=f"Novo lead: {lead.name}",
        html_body=f"""
            <h2>Novo lead cadastrado</h2>
            <p><strong>Nome:</strong> {lead.name}</p>
            <p><strong>E-mail:</strong> {lead.email}</p>
            <p><strong>Telefone:</strong> {lead.phone or '—'}</p>
            <p><strong>Origem:</strong> {lead.source or '—'}</p>
            <p><strong>Investimento:</strong> {f"R$ {lead.budget:,.2f}" if lead.budget else "—"}</p>
        """,
    )

    if lead.phone:
        send_sms(
            to=lead.phone,
            body=f"Olá, {lead.name}! Recebemos seu contato e em breve nossa equipe entrará em toque.",
        )


def notify_lead_moved(lead, stage_name: str) -> None:
    """Dispara ao mover um lead para etapas importantes do pipeline."""
    if stage_name not in STAGES_TO_NOTIFY:
        return

    notify_email = os.getenv("NOTIFY_EMAIL", "equipe@agencia.com")
    send_email(
        to=notify_email,
        subject=f"Lead '{lead.name}' avançou para '{stage_name}'",
        html_body=f"""
            <h2>Lead avançou no pipeline</h2>
            <p><strong>Nome:</strong> {lead.name}</p>
            <p><strong>E-mail:</strong> {lead.email}</p>
            <p><strong>Telefone:</strong> {lead.phone or '—'}</p>
            <p><strong>Nova etapa:</strong> <strong>{stage_name}</strong></p>
        """,
    )

    if stage_name == "fechado":
        notify_phone = os.getenv("NOTIFY_PHONE", "+5511999990000")
        send_sms(
            to=notify_phone,
            body=f"Negócio fechado! Lead: {lead.name} ({lead.email})",
        )
