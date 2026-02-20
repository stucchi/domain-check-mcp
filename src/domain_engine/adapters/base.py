from __future__ import annotations

from abc import ABC, abstractmethod

from domain_engine.models import DomainCheckResult


class TLDAdapter(ABC):
    @property
    @abstractmethod
    def tld(self) -> str: ...

    @abstractmethod
    def check(self, domain: str) -> DomainCheckResult: ...
