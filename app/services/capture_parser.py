"""
Parser inteligente de payloads de captura de leads.

Suporta:
  - Meta Lead Ads  (formato entry/changes/field_data)
  - Formulários customizados (dict plano)
  - Landing pages  (first_name + last_name, variações de campo)
"""

import re
from typing import Any

# ── Aliases de campos ────────────────────────────────────────────────────────

_NAME_KEYS = [
    "full_name", "name", "nome", "nome_completo", "fullname",
    "contact_name", "nome_do_contato",
]
_FIRST_KEYS = ["first_name", "primeiro_nome", "firstname", "fname"]
_LAST_KEYS  = ["last_name", "sobrenome", "lastname", "lname"]
_EMAIL_KEYS = ["email", "e-mail", "email_address", "email_do_contato", "contact_email"]
_PHONE_KEYS = [
    "phone", "phone_number", "telefone", "tel", "celular",
    "mobile", "whatsapp", "fone", "phone_number",
]

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z0-9.\-]+$")
_PHONE_STRIP = re.compile(r"[^\d]")


# ── Detecção de fonte ─────────────────────────────────────────────────────────

def detect_source(payload: dict) -> str:
    """Identifica o formato do payload."""
    if "entry" in payload and isinstance(payload.get("entry"), list):
        try:
            if payload["entry"][0]["changes"][0]["field"] == "leadgen":
                return "meta_lead_ads"
        except (KeyError, IndexError, TypeError):
            pass
    if any(k in payload for k in _FIRST_KEYS + _LAST_KEYS):
        return "landing_page"
    return "custom"


# ── Extratores por formato ────────────────────────────────────────────────────

def _extract_meta(payload: dict) -> dict:
    try:
        value = payload["entry"][0]["changes"][0]["value"]
    except (KeyError, IndexError, TypeError):
        return {}

    fd: dict[str, str] = {}
    for item in value.get("field_data", []):
        key = (item.get("name") or "").lower().replace(" ", "_")
        vals = item.get("values") or []
        if vals:
            fd[key] = vals[0]

    result: dict[str, Any] = {
        "external_source_id": str(value.get("leadgen_id", "")),
        "campaign_name":      value.get("campaign_name"),
        "adset_name":         value.get("adset_name"),
        "ad_name":            value.get("ad_name"),
    }

    result["email"] = _first(fd, _EMAIL_KEYS)
    result["phone"] = _first(fd, _PHONE_KEYS)

    # nome: campo direto ou first+last
    result["name"] = _first(fd, _NAME_KEYS) or _join_name(
        _first(fd, _FIRST_KEYS), _first(fd, _LAST_KEYS)
    )

    # UTMs vindos do field_data (ex.: "utm_source")
    for utm in ("utm_source", "utm_campaign", "utm_medium", "utm_content", "utm_term"):
        result[utm] = fd.get(utm) or value.get(utm)

    return result


def _extract_flat(payload: dict) -> dict:
    flat = {k.lower().replace("-", "_"): v for k, v in payload.items()}

    name = _first(flat, _NAME_KEYS) or _join_name(
        _first(flat, _FIRST_KEYS), _first(flat, _LAST_KEYS)
    )

    result: dict[str, Any] = {
        "name":  name,
        "email": _first(flat, _EMAIL_KEYS),
        "phone": _first(flat, _PHONE_KEYS),
        "source": flat.get("source") or flat.get("origem"),
        "budget": _to_float(flat.get("budget") or flat.get("investimento")),
        "external_source_id": str(flat.get("external_source_id") or flat.get("id") or ""),
    }

    for utm in ("utm_source", "utm_campaign", "utm_medium", "utm_content", "utm_term"):
        result[utm] = flat.get(utm)

    return result


# ── API pública ───────────────────────────────────────────────────────────────

class ParseError(ValueError):
    pass


def parse(payload: dict) -> tuple[dict, str]:
    """
    Retorna (campos_extraidos, source_detectado).
    Lança ParseError se campos obrigatórios estiverem ausentes ou inválidos.
    """
    source = detect_source(payload)

    if source == "meta_lead_ads":
        fields = _extract_meta(payload)
    else:
        fields = _extract_flat(payload)

    # Normalizar e validar e-mail
    email = (fields.get("email") or "").strip().lower()
    if not email:
        raise ParseError("Campo 'email' não encontrado no payload.")
    if not _EMAIL_RE.match(email):
        raise ParseError(f"E-mail inválido: {email!r}")
    fields["email"] = email

    # Normalizar nome
    name = (fields.get("name") or "").strip()
    if not name:
        raise ParseError("Campo 'name' não encontrado no payload.")
    fields["name"] = name

    # Normalizar telefone
    phone = normalize_phone(fields.get("phone") or "")
    fields["phone"] = phone or None

    # Limpar chaves None para não poluir o upsert
    fields = {k: v for k, v in fields.items() if v is not None and v != ""}

    return fields, source


# ── Helpers internos ──────────────────────────────────────────────────────────

def _first(d: dict, keys: list[str]) -> str | None:
    for k in keys:
        v = d.get(k)
        if v and str(v).strip():
            return str(v).strip()
    return None


def _join_name(first: str | None, last: str | None) -> str | None:
    parts = [p for p in (first, last) if p]
    return " ".join(parts) if parts else None


def _to_float(v: Any) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def normalize_phone(raw: str) -> str:
    if not raw:
        return ""
    cleaned = _PHONE_STRIP.sub("", raw)
    # reintroduz o + inicial se o original começava com +
    if raw.lstrip().startswith("+"):
        cleaned = "+" + cleaned
    return cleaned if len(cleaned.lstrip("+")) >= 8 else ""
