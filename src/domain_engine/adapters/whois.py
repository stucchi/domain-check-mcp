from __future__ import annotations

import socket

from domain_engine.exceptions import DomainCheckError, RateLimitedError
from domain_engine.models import DomainCheckResult

from .base import TLDAdapter


class WhoisAdapter(TLDAdapter):
    """WHOIS-based adapter for TLDs without RDAP support."""

    def __init__(
        self,
        tld: str,
        whois_server: str,
        not_found_pattern: str,
        timeout: float = 10.0,
    ) -> None:
        self._tld = tld
        self._whois_server = whois_server
        self._not_found_pattern = not_found_pattern.lower()
        self._timeout = timeout

    @property
    def tld(self) -> str:
        return self._tld

    def check(self, domain: str) -> DomainCheckResult:
        try:
            raw_response = self._query(domain)
        except socket.timeout:
            raise DomainCheckError(f"WHOIS request timed out for {domain}")
        except OSError as exc:
            raise DomainCheckError(f"WHOIS connection failed for {domain}: {exc}")

        lower = raw_response.lower()
        if "number of allowed queries exceeded" in lower or "queries exceeded" in lower:
            raise RateLimitedError(
                f"Rate limited by .{self._tld} registry while checking {domain}. "
                "This registry has aggressive rate limits — try again in a few minutes."
            )

        if self._not_found_pattern in lower:
            return DomainCheckResult(
                domain=domain,
                available=True,
                status="available",
            )

        return DomainCheckResult(
            domain=domain,
            available=False,
            status="registered",
        )

    def _query(self, domain: str) -> str:
        with socket.create_connection(
            (self._whois_server, 43), timeout=self._timeout
        ) as sock:
            sock.sendall(f"{domain}\r\n".encode())
            chunks = []
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                chunks.append(data)
        return b"".join(chunks).decode("utf-8", errors="replace")
