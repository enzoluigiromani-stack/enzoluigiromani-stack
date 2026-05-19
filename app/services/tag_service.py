"""
Sistema de tags automáticas aplicadas a leads na captura.

Tags disponíveis:
  facebook    → via Meta Lead Ads ou utm_source facebook/instagram
  google      → utm_source google/adwords
  tiktok      → utm_source tiktok
  organic     → tráfego orgânico (sem utm_medium pago)
  paid        → utm_medium cpc/ppc/cpm
  high_ticket → budget >= HIGH_TICKET_THRESHOLD
  referral    → utm_medium referral / utm_source indicacao
"""

HIGH_TICKET_THRESHOLD = 5000.0

_FACEBOOK_SOURCES = {"facebook", "fb", "instagram", "ig", "meta"}
_GOOGLE_SOURCES   = {"google", "google-ads", "adwords", "googleads", "google_ads"}
_TIKTOK_SOURCES   = {"tiktok", "tiktokads", "tiktok_ads", "ttads"}
_PAID_MEDIUMS     = {"cpc", "ppc", "paid", "cpm", "paidsocial", "paid_social"}
_REFERRAL_SOURCES = {"indicacao", "referral", "partner", "parceiro"}


def compute_tags(fields: dict) -> list[str]:
    """
    Calcula e retorna a lista de tags para o lead baseado nos campos extraídos.
    Idempotente: pode ser chamado a qualquer momento.
    """
    tags: list[str] = []

    utm_source   = (fields.get("utm_source")   or "").lower().strip()
    utm_medium   = (fields.get("utm_medium")   or "").lower().strip()
    source       = (fields.get("source")       or "").lower().strip()
    campaign     = (fields.get("campaign_name") or "").lower().strip()
    budget       = fields.get("budget") or 0

    # ── Plataforma de origem ──────────────────────────────────────────────────
    if source == "meta_lead_ads" or utm_source in _FACEBOOK_SOURCES:
        tags.append("facebook")

    if utm_source in _GOOGLE_SOURCES:
        tags.append("google")

    if utm_source in _TIKTOK_SOURCES:
        tags.append("tiktok")

    # ── Tipo de tráfego ───────────────────────────────────────────────────────
    if utm_medium in _PAID_MEDIUMS:
        tags.append("paid")
    elif utm_medium == "organic" or (
        not utm_source and not campaign and utm_medium not in _PAID_MEDIUMS
    ):
        tags.append("organic")

    if utm_medium == "referral" or utm_source in _REFERRAL_SOURCES:
        tags.append("referral")

    # ── Valor potencial ───────────────────────────────────────────────────────
    if budget and float(budget) >= HIGH_TICKET_THRESHOLD:
        tags.append("high_ticket")

    return tags


def merge_tags(existing: list[str] | None, new_tags: list[str]) -> list[str]:
    """Une tags antigas com novas sem duplicar."""
    combined = set(existing or []) | set(new_tags)
    return sorted(combined)
