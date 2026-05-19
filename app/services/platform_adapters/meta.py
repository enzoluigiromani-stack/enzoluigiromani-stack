"""Adaptador para Meta Lead Ads (Facebook/Instagram)."""

from .base import BasePlatformAdapter, NormalizedLead
from app.services.capture_parser import normalize_phone, _first, _join_name

_NAME_KEYS  = ["full_name", "name", "nome", "nome_completo"]
_FIRST_KEYS = ["first_name", "primeiro_nome"]
_LAST_KEYS  = ["last_name", "sobrenome"]
_EMAIL_KEYS = ["email", "email_address"]
_PHONE_KEYS = ["phone_number", "phone", "telefone", "celular", "whatsapp"]


class MetaLeadAdsAdapter(BasePlatformAdapter):
    SOURCE_NAME = "meta_lead_ads"

    def detect(self, payload: dict) -> bool:
        try:
            return payload["entry"][0]["changes"][0]["field"] == "leadgen"
        except (KeyError, IndexError, TypeError):
            return False

    def extract(self, payload: dict) -> NormalizedLead:
        try:
            value = payload["entry"][0]["changes"][0]["value"]
        except (KeyError, IndexError, TypeError):
            value = {}

        fd: dict[str, str] = {}
        for item in value.get("field_data", []):
            key = (item.get("name") or "").lower().replace(" ", "_")
            vals = item.get("values") or []
            if vals:
                fd[key] = vals[0]

        name = _first(fd, _NAME_KEYS) or _join_name(
            _first(fd, _FIRST_KEYS), _first(fd, _LAST_KEYS)
        ) or ""

        utm_source = fd.get("utm_source") or value.get("utm_source")

        return NormalizedLead(
            name               = name,
            email              = _first(fd, _EMAIL_KEYS) or "",
            phone              = normalize_phone(_first(fd, _PHONE_KEYS) or ""),
            source             = self.SOURCE_NAME,
            utm_source         = utm_source or "facebook",
            utm_campaign       = fd.get("utm_campaign") or value.get("utm_campaign"),
            utm_medium         = fd.get("utm_medium") or value.get("utm_medium") or "paid",
            utm_content        = fd.get("utm_content"),
            utm_term           = fd.get("utm_term"),
            campaign_name      = value.get("campaign_name"),
            adset_name         = value.get("adset_name"),
            ad_name            = value.get("ad_name"),
            external_source_id = str(value.get("leadgen_id", "")),
        )

    @staticmethod
    def build_test_envelope(
        name: str,
        email: str,
        phone: str | None = None,
        leadgen_id: str = "test_000",
        campaign_name: str | None = None,
        adset_name: str | None = None,
        ad_name: str | None = None,
        utm_campaign: str | None = None,
        **extra,
    ) -> dict:
        """Monta um payload Meta Lead Ads válido para testes."""
        field_data = [
            {"name": "full_name", "values": [name]},
            {"name": "email",     "values": [email]},
        ]
        if phone:
            field_data.append({"name": "phone_number", "values": [phone]})
        if utm_campaign:
            field_data.append({"name": "utm_campaign", "values": [utm_campaign]})
        for k, v in extra.items():
            if v is not None:
                field_data.append({"name": k, "values": [str(v)]})

        return {
            "object": "page",
            "entry": [{
                "id": "TEST_PAGE",
                "changes": [{
                    "field": "leadgen",
                    "value": {
                        "leadgen_id":    leadgen_id,
                        "campaign_name": campaign_name or "Teste Campanha",
                        "adset_name":    adset_name    or "Teste Adset",
                        "ad_name":       ad_name       or "Teste Ad",
                        "field_data":    field_data,
                    },
                }],
            }],
        }
