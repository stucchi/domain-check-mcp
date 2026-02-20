from __future__ import annotations

import httpx

from domain_engine.exceptions import DomainCheckError, RateLimitedError
from domain_engine.models import DomainCheckResult

from .base import TLDAdapter

RDAP_URL = "https://rdap.verisign.com/com/v1/domain/{domain}"


class ComAdapter(TLDAdapter):
    def __init__(self, timeout: float = 10.0) -> None:
        self._timeout = timeout

    @property
    def tld(self) -> str:
        return "com"

    def check(self, domain: str) -> DomainCheckResult:
        url = RDAP_URL.format(domain=domain)
        try:
            resp = httpx.get(url, timeout=self._timeout)
        except httpx.TimeoutException:
            raise DomainCheckError(f"RDAP request timed out for {domain}")

        if resp.status_code == 404:
            return DomainCheckResult(
                domain=domain,
                available=True,
                status="available",
            )

        if resp.status_code == 429:
            raise RateLimitedError(f"Rate limited while checking {domain}")

        if resp.status_code == 200:
            return DomainCheckResult(
                domain=domain,
                available=False,
                status="registered",
                raw=resp.json(),
            )

        raise DomainCheckError(
            f"Unexpected RDAP response {resp.status_code} for {domain}"
        )
