"""
Adaptador para Google Lead Form Extensions.

Payload de referência:
{
  "lead_id": "...",
  "campaign_id": "...",
  "campaign_name": "...",
  "google_key": "...",
  "user_column_data": [
    {"column_id": "FULL_NAME",    "string_value": "..."},
    {"column_id": "EMAIL",        "string_value": "..."},
    {"column_id": "PHONE_NUMBER", "string_value": "..."}
  ]
}
"""

from .base import BasePlatformAdapter, NormalizedLead
from app.services.capture_parser import normalize_phone, _join_name

_COLUMN_MAP = {
    "FULL_NAME":    "name",
    "GIVEN_NAME":   "first_name",
    "FAMILY_NAME":  "last_name",
    "EMAIL":        "email",
    "PHONE_NUMBER": "phone",
    "CITY":         "city",
    "COUNTRY":      "country",
}


class GoogleLeadFormsAdapter(BasePlatformAdapter):
    SOURCE_NAME = "google_lead_forms"

    def detect(self, payload: dict) -> bool:
        return "user_column_data" in payload and "lead_id" in payload

    def extract(self, payload: dict) -> NormalizedLead:
        cols: dict[str, str] = {}
        for item in payload.get("user_column_data", []):
            col_id = item.get("column_id", "")
            key    = _COLUMN_MAP.get(col_id, col_id.lower())
            cols[key] = item.get("string_value", "")

        name = cols.get("name") or _join_name(
            cols.get("first_name"), cols.get("last_name")
        ) or ""

        return NormalizedLead(
            name               = name,
            email              = cols.get("email", ""),
            phone              = normalize_phone(cols.get("phone", "")),
            source             = self.SOURCE_NAME,
            utm_source         = "google",
            utm_medium         = "cpc",
            campaign_name      = payload.get("campaign_name"),
            external_source_id = str(payload.get("lead_id", "")),
        )
