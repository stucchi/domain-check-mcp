from __future__ import annotations

import httpx

from domain_engine.exceptions import DomainCheckError, RateLimitedError
from domain_engine.models import DomainCheckResult

from .base import TLDAdapter


class RDAPAdapter(TLDAdapter):
    """Generic RDAP adapter — works with any TLD given its RDAP base URL."""

    def __init__(self, tld: str, rdap_base_url: str, timeout: float = 10.0) -> None:
        self._tld = tld
        self._rdap_base_url = rdap_base_url.rstrip("/")
        self._timeout = timeout

    @property
    def tld(self) -> str:
        return self._tld

    def check(self, domain: str) -> DomainCheckResult:
        url = f"{self._rdap_base_url}/domain/{domain}"
        try:
            resp = httpx.get(url, timeout=self._timeout, follow_redirects=True)
        except httpx.TimeoutException:
            raise DomainCheckError(f"RDAP request timed out for {domain}")
        except httpx.ConnectError:
            raise DomainCheckError(f"RDAP connection failed for {domain}")

        if resp.status_code == 404:
            return DomainCheckResult(
                domain=domain,
                available=True,
                status="available",
            )

        if resp.status_code == 429:
            raise RateLimitedError(f"Rate limited while checking {domain}. Try again later.")

        if resp.status_code == 403:
            body = resp.text.lower()
            if "number of allowed queries exceeded" in body or "rate" in body:
                raise RateLimitedError(
                    f"Rate limited by .{self._tld} registry while checking {domain}. "
                    "This registry has aggressive rate limits — try again in a few minutes."
                )
            raise DomainCheckError(
                f"Access denied (403) by .{self._tld} registry for {domain}"
            )

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
