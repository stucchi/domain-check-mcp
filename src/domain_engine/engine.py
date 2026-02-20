from __future__ import annotations

import re

from domain_engine.adapters.base import TLDAdapter
from domain_engine.adapters.com import ComAdapter
from domain_engine.exceptions import InvalidDomainError, UnsupportedTLDError
from domain_engine.models import DomainCheckResult

_DOMAIN_RE = re.compile(
    r"^(?!-)([a-z0-9-]{1,63})(?<!-)\.([a-z]{2,})$"
)


class DomainCheckEngine:
    def __init__(self) -> None:
        self._adapters: dict[str, TLDAdapter] = {}

    def register_adapter(self, adapter: TLDAdapter) -> None:
        self._adapters[adapter.tld] = adapter

    @property
    def supported_tlds(self) -> list[str]:
        return list(self._adapters)

    def check(self, domain: str) -> DomainCheckResult:
        domain = domain.strip().lower()
        match = _DOMAIN_RE.match(domain)
        if not match:
            raise InvalidDomainError(f"Invalid domain: {domain}")

        tld = match.group(2)
        adapter = self._adapters.get(tld)
        if adapter is None:
            raise UnsupportedTLDError(
                f"No adapter for .{tld} — supported: {', '.join(f'.{t}' for t in self._adapters)}"
            )

        return adapter.check(domain)


def create_engine() -> DomainCheckEngine:
    engine = DomainCheckEngine()
    engine.register_adapter(ComAdapter())
    return engine
