"""Contrato base para todos os adaptadores de plataforma."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class NormalizedLead:
    """Campos padronizados extraídos por qualquer adaptador."""
    name:               str
    email:              str
    phone:              str | None       = None
    source:             str | None       = None
    budget:             float | None     = None
    utm_source:         str | None       = None
    utm_campaign:       str | None       = None
    utm_medium:         str | None       = None
    utm_content:        str | None       = None
    utm_term:           str | None       = None
    campaign_name:      str | None       = None
    adset_name:         str | None       = None
    ad_name:            str | None       = None
    external_source_id: str | None       = None
    extra:              dict             = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = {k: v for k, v in self.__dict__.items() if v is not None and k != "extra"}
        d.update(self.extra)
        return d


class BasePlatformAdapter(ABC):
    """Adaptador de plataforma de captura de leads."""

    SOURCE_NAME: str = "unknown"

    @abstractmethod
    def detect(self, payload: dict) -> bool:
        """Retorna True se este adaptador reconhece o payload."""
        ...

    @abstractmethod
    def extract(self, payload: dict) -> NormalizedLead:
        """Extrai e normaliza os dados do payload."""
        ...
