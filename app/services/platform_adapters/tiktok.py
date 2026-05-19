"""
Adaptador para TikTok Lead Generation Ads.

Payload de referência:
{
  "advertiser_id": "...",
  "form_id": "...",
  "data": {
    "lead_id": "...",
    "create_time": 1234567890,
    "field_value_map": {
      "first_name":   "...",
      "last_name":    "...",
      "email":        "...",
      "phone_number": "..."
    }
  }
}
"""

from .base import BasePlatformAdapter, NormalizedLead
from app.services.capture_parser import normalize_phone, _join_name


class TikTokAdsAdapter(BasePlatformAdapter):
    SOURCE_NAME = "tiktok_ads"

    def detect(self, payload: dict) -> bool:
        return (
            "advertiser_id" in payload
            and isinstance(payload.get("data"), dict)
            and "field_value_map" in payload.get("data", {})
        )

    def extract(self, payload: dict) -> NormalizedLead:
        data = payload.get("data", {})
        fv   = data.get("field_value_map", {})

        name = fv.get("full_name") or _join_name(
            fv.get("first_name"), fv.get("last_name")
        ) or ""

        return NormalizedLead(
            name               = name,
            email              = fv.get("email", ""),
            phone              = normalize_phone(fv.get("phone_number") or fv.get("phone", "")),
            source             = self.SOURCE_NAME,
            utm_source         = "tiktok",
            utm_medium         = "paid",
            external_source_id = str(data.get("lead_id", "")),
        )
