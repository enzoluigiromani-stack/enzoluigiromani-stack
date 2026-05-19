"""
Registro de adaptadores de plataforma.

Adicionar um novo adaptador:
1. Crie o arquivo em platform_adapters/<plataforma>.py
2. Implemente BasePlatformAdapter
3. Adicione à lista ADAPTERS abaixo

A ordem importa: o primeiro que retornar detect() = True é usado.
Plataformas mais específicas (Meta, TikTok) devem vir antes das genéricas (Zapier, n8n).
"""

from .meta    import MetaLeadAdsAdapter
from .google  import GoogleLeadFormsAdapter
from .tiktok  import TikTokAdsAdapter
from .zapier  import ZapierAdapter
from .n8n     import N8nAdapter
from .base    import BasePlatformAdapter, NormalizedLead

ADAPTERS: list[BasePlatformAdapter] = [
    MetaLeadAdsAdapter(),
    GoogleLeadFormsAdapter(),
    TikTokAdsAdapter(),
    ZapierAdapter(),
    N8nAdapter(),
]


def get_adapter(payload: dict) -> BasePlatformAdapter | None:
    """Retorna o adaptador adequado para o payload, ou None se nenhum detectar."""
    for adapter in ADAPTERS:
        if adapter.detect(payload):
            return adapter
    return None


__all__ = [
    "ADAPTERS",
    "get_adapter",
    "BasePlatformAdapter",
    "NormalizedLead",
    "MetaLeadAdsAdapter",
    "GoogleLeadFormsAdapter",
    "TikTokAdsAdapter",
    "ZapierAdapter",
    "N8nAdapter",
]
