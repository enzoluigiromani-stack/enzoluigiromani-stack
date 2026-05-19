"""
Adaptador para Zapier Zaps.

Zapier envia flat JSON com qualquer estrutura de campos.
Este adaptador apenas marca a origem como 'zapier' e deixa
o capture_parser fazer a extração dos campos padrão.

Payload típico de um Zap:
{
  "zap_id": "12345678",
  "name": "João Silva",
  "email": "joao@exemplo.com",
  "phone": "11912345678",
  "utm_source": "facebook",
  ...
}
"""

from .base import BasePlatformAdapter, NormalizedLead
from app.services.capture_parser import _first, normalize_phone, _join_name

_NAME_KEYS  = ["name", "nome", "full_name", "contact_name"]
_FIRST_KEYS = ["first_name", "firstname", "primeiro_nome"]
_LAST_KEYS  = ["last_name", "lastname", "sobrenome"]
_EMAIL_KEYS = ["email", "e-mail", "email_address"]
_PHONE_KEYS = ["phone", "telefone", "tel", "celular", "whatsapp", "mobile"]


class ZapierAdapter(BasePlatformAdapter):
    SOURCE_NAME = "zapier"

    def detect(self, payload: dict) -> bool:
        flat = {k.lower(): v for k, v in payload.items()}
        return "zap_id" in flat or "zapier_id" in flat or "zap_name" in flat

    def extract(self, payload: dict) -> NormalizedLead:
        flat = {k.lower().replace("-", "_"): v for k, v in payload.items()}

        name = _first(flat, _NAME_KEYS) or _join_name(
            _first(flat, _FIRST_KEYS), _first(flat, _LAST_KEYS)
        ) or ""

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
            external_source_id = str(flat.get("zap_id") or flat.get("zapier_id") or ""),
        )
