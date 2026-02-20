from __future__ import annotations


class DomainCheckError(Exception):
    pass


class UnsupportedTLDError(DomainCheckError):
    pass


class RateLimitedError(DomainCheckError):
    pass


class InvalidDomainError(DomainCheckError):
    pass
