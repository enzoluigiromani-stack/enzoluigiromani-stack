"""
Adaptador para n8n workflows.

n8n pode enviar payloads em vários formatos dependendo do workflow.
Este adaptador detecta execuções n8n pelo header ou campo de execução
e normaliza usando as mesmas regras do custom parser.

Payload típico (nó HTTP Request do n8n):
{
  "execution_id": "exec_abc123",
  "workflow_id": "wf_456",
  "name": "Maria Santos",
  "email": "maria@agencia.com",
  "phone": "+5521999887766",
  "utm_source": "instagram"
}
"""

from .base import BasePlatformAdapter, NormalizedLead
from app.services.capture_parser import _first, normalize_phone, _join_name

_NAME_KEYS  = ["name", "nome", "full_name", "contact_name"]
_FIRST_KEYS = ["first_name", "firstname"]
_LAST_KEYS  = ["last_name", "lastname"]
_EMAIL_KEYS = ["email", "e-mail", "email_address"]
_PHONE_KEYS = ["phone", "telefone", "tel", "celular", "whatsapp", "mobile"]

_N8N_MARKERS = {"execution_id", "workflow_id", "n8n_execution_id", "n8n_workflow_id"}


class N8nAdapter(BasePlatformAdapter):
    SOURCE_NAME = "n8n"

    def detect(self, payload: dict) -> bool:
        flat = {k.lower() for k in payload}
        return bool(flat & _N8N_MARKERS)

    def extract(self, payload: dict) -> NormalizedLead:
        flat = {k.lower().replace("-", "_"): v for k, v in payload.items()}

        name = _first(flat, _NAME_KEYS) or _join_name(
            _first(flat, _FIRST_KEYS), _first(flat, _LAST_KEYS)
        ) or ""

        exec_id = (
            flat.get("execution_id")
            or flat.get("n8n_execution_id")
            or ""
        )

        return NormalizedLead(
            name               = name,
            email              = _first(flat, _EMAIL_KEYS) or "",
            phone              = normalize_phone(_first(flat, _PHONE_KEYS) or ""),
            source             = self.SOURCE_NAME,
            utm_source         = flat.get("utm_source"),
            utm_campaign       = flat.get("utm_campaign"),
            utm_medium         = flat.get("utm_medium"),
            utm_content        = flat.get("utm_content"),
            utm_term           = flat.get("utm_term"),
            campaign_name      = flat.get("campaign_name"),
            external_source_id = str(exec_id),
        )
