from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DomainCheckResult:
    domain: str
    available: bool
    status: str
    raw: dict | None = field(default=None, repr=False)

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "available": self.available,
            "status": self.status,
        }
